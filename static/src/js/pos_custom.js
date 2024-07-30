/** @odoo-module **/

import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { ProductsWidget } from '@point_of_sale/app/screens/product_screen/product_list/product_list';
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { VariantInfoPopup } from "@om_hospital/js/pos_variant_pop";
import { patch } from '@web/core/utils/patch';
import { PosDB } from '@point_of_sale/app/store/db';
import { PosStore } from '@point_of_sale/app/store/pos_store';
import { markRaw } from "@odoo/owl";
import { Mutex } from "@web/core/utils/concurrency";
import { PosCollection, Order, Product } from "@point_of_sale/app/store/models";
import { unaccent } from "@web/core/utils/strings";
import {
    formatDate,
    formatDateTime,
    serializeDateTime,
    deserializeDate,
    deserializeDateTime,
} from "@web/core/l10n/dates";
const { DateTime } = luxon;

// Patch Product for override function: get_price,
patch(Product.prototype,{
    get_price(pricelist, quantity, price_extra = 0, recurring = false) {
        const date = DateTime.now();

        // In case of nested pricelists, it is necessary that all pricelists are made available in
        // the POS. Display a basic alert to the user in the case where there is a pricelist item
        // but we can't load the base pricelist to get the price when calling this method again.
        // As this method is also call without pricelist available in the POS, we can't just check
        // the absence of pricelist.
        if (recurring && !pricelist) {
            alert(
                _t(
                    "An error occurred when loading product prices. " +
                        "Make sure all pricelists are available in the POS."
                )
            );
        }

        const rules = !pricelist
            ? []
            : (this.applicablePricelistItems[pricelist.id] || []).filter((item) =>
                  this.isPricelistItemUsable(item, date)
              );

        let price = this.list_price + (price_extra || 0);
        const rule = rules.find((rule) => !rule.min_quantity || quantity >= rule.min_quantity);
        if (!rule) {
            return price;
        }

        if (rule.base === "pricelist") {
            const base_pricelist = this.pos.pricelists.find(
                (pricelist) => pricelist.id === rule.base_pricelist_id[0]
            );
            if (base_pricelist) {
                price = this.get_price(base_pricelist, quantity, 0, true);
            }
        } else if (rule.base === "standard_price") {
            price = this.standard_price;
        }

        if (rule.compute_price === "fixed") {
            price = rule.fixed_price;
        } else if (rule.compute_price === "percentage") {
            price = price - price * (rule.percent_price / 100);
        } else {
            var price_limit = price;
            price -= price * (rule.price_discount / 100);
            if (rule.price_round) {
                price = round_pr(price, rule.price_round);
            }
            if (rule.price_surcharge) {
                price += rule.price_surcharge;
            }
            if (rule.price_min_margin) {
                price = Math.max(price, price_limit + rule.price_min_margin);
            }
            if (rule.price_max_margin) {
                price = Math.min(price, price_limit + rule.price_max_margin);
            }
        }
        return price;
    },
})

// Patch PosDB for override function: get_product_variants, add_products
patch(PosDB.prototype, {
    get_product_variants(templateId) {
        console.log('ORM', this.orm);
        if (!templateId) return [];

        return Object.values(this.product_by_id).filter(
            (product) => product.product_tmpl_id === templateId && product.id !== templateId
        );
    },
    add_products(products) {
        var stored_categories = this.product_by_category_id;

        if (!(products instanceof Array)) {
            products = [products];
        }
        for (var i = 0, len = products.length; i < len; i++) {
            var product = products[i];
            if (product.id in this.product_by_id) {
                continue;
            }
            if (product.available_in_pos) {
                var search_string = unaccent(this._product_search_string(product));
                const all_categ_ids = product.pos_categ_ids.length
                    ? product.pos_categ_ids
                    : [this.root_category_id];
                product.product_variant_id = product.product_variant_id[0];
                for (const categ_id of all_categ_ids) {
                    if (!stored_categories[categ_id]) {
                        stored_categories[categ_id] = [];
                    }
                    stored_categories[categ_id].push(product.id);

                    if (this.category_search_string[categ_id] === undefined) {
                        this.category_search_string[categ_id] = "";
                    }
                    this.category_search_string[categ_id] += search_string;

                    var ancestors = this.get_category_ancestors_ids(categ_id) || [];

                    for (var j = 0, jlen = ancestors.length; j < jlen; j++) {
                        var ancestor = ancestors[j];
                        if (!stored_categories[ancestor]) {
                            stored_categories[ancestor] = [];
                        }
                        stored_categories[ancestor].push(product.id);

                        if (this.category_search_string[ancestor] === undefined) {
                            this.category_search_string[ancestor] = "";
                        }
                        this.category_search_string[ancestor] += search_string;
                    }
                }
            }
            this.product_by_id[product.id] = product;
            if (product.barcode && product.active) {
                this.product_by_barcode[product.barcode] = product;
            }
        }
    }
});

// Patch PosStore for override function: setup, fetchProductTemplates, load_server_data, _processData, _loadProductProduct, getProductInfo
patch(PosStore.prototype, {
    async setup(env, { popup, orm, number_buffer, hardware_proxy, barcode_reader, ui }) {
        this.env = env;
        this.orm = orm;
        this.popup = popup;
        this.numberBuffer = number_buffer;
        this.barcodeReader = barcode_reader;
        this.ui = ui;

        this.db = new PosDB(); // a local database used to search trough products and categories & store pending orders
        this.unwatched = markRaw({});
        this.pushOrderMutex = new Mutex();

        // Business data; loaded from the server at launch
        this.company_logo = null;
        this.company_logo_base64 = "";
        this.currency = null;
        this.company = null;
        this.user = null;
        this.partners = [];
        this.taxes = [];
        this.pos_session = null;
        this.config = null;
        this.units = [];
        this.units_by_id = {};
        this.uom_unit_id = null;
        this.default_pricelist = null;
        this.order_sequence = 1;
        this.printers_category_ids_set = new Set();

        // Object mapping the order's name (which contains the uid) to it's server_id after
        // validation (order paid then sent to the backend).
        this.validated_orders_name_server_id_map = {};

        this.numpadMode = "quantity";
        this.mobile_pane = "right";
        this.ticket_screen_mobile_pane = "left";
        this.productListView = window.localStorage.getItem("productListView") || "grid";

        // Record<orderlineId, { 'qty': number, 'orderline': { qty: number, refundedQty: number, orderUid: string }, 'destinationOrderUid': string }>
        this.toRefundLines = {};
        this.TICKET_SCREEN_STATE = {
            syncedOrders: {
                currentPage: 1,
                cache: {},
                toShow: [],
                nPerPage: 80,
                totalCount: null,
                cacheDate: null,
            },
            ui: {
                selectedOrder: null,
                searchDetails: this.getDefaultSearchDetails(),
                filter: null,
                // maps the order's backendId to it's selected orderline
                selectedOrderlineIds: {},
                highlightHeaderNote: false,
            },
        };

        this.ordersToUpdateSet = new Set(); // used to know which orders need to be sent to the back end when syncing
        this.loadingOrderState = false; // used to prevent orders fetched to be put in the update set during the reactive change
        this.showOfflineWarning = true; // Allows to avoid the display of the offline popup when the user has already had it.
        this.tempScreenIsShown = false;

        // these dynamic attributes can be watched for change by other models or widgets
        Object.assign(this, {
            synch: { status: "connected", pending: 0 },
            orders: new PosCollection(),
            selectedOrder: null,
            selectedPartner: null,
            selectedCategoryId: null,
            searchProductWord: "",
        });

        this.ready = new Promise((resolve) => {
            this.markReady = resolve;
        });

        this.hardwareProxy = hardware_proxy;
        this.hardwareProxy.pos = this;
        await this.load_server_data();
        if (this.config.use_proxy) {
            await this.connectToProxy();
        }
        this.closeOtherTabs();
        this.preloadImages();
        this.showScreen("ProductScreen");
    },
    async fetchProductTemplates() {
        try {
            const productTemplates = await this.orm.silent.call("product.template", "get_product_templates", []);
            console.log("Templates", productTemplates);
            return productTemplates;
        } catch (error) {
            console.error('Error fetching product templates:', error);
            return [];
        }
    },
    async load_server_data() {
        try {
            const loadedData = await this.orm.silent.call("pos.session", "load_pos_data", [
                [odoo.pos_session_id],
            ]);
            if (!loadedData) {
                console.error('Failed to load server data.');
                return;
            }

            const productTemplates = await this.fetchProductTemplates();
            loadedData['product.template'] = productTemplates;
            console.log('Loaded Data:', loadedData);

            await this._processData(loadedData);
            await this.after_load_server_data();
        } catch (error) {
            console.error('Error loading server data:', error);
        }
    },
    async _processData(loadedData) {
        this.version = loadedData["version"];
        this.company = loadedData["res.company"];
        this.dp = loadedData["decimal.precision"];
        this.units = loadedData["uom.uom"];
        this.units_by_id = loadedData["units_by_id"];
        this.states = loadedData["res.country.state"];
        this.countries = loadedData["res.country"];
        this.langs = loadedData["res.lang"];
        this.taxes = loadedData["account.tax"];
        this.taxes_by_id = loadedData["taxes_by_id"];
        this.pos_session = loadedData["pos.session"];
        this._loadPosSession();
        this.config = loadedData["pos.config"];
        this._loadPoSConfig();
        this.bills = loadedData["pos.bill"];
        this.partners = loadedData["res.partner"];
        this.addPartners(this.partners);
        this.picking_type = loadedData["stock.picking.type"];
        this.user = loadedData["res.users"];
        this.pricelists = loadedData["product.pricelist"];
        this.default_pricelist = loadedData["default_pricelist"];
        this.currency = loadedData["res.currency"];
        this.db.add_attributes(loadedData["attributes_by_ptal_id"]);
        this.db.add_categories(loadedData["pos.category"]);
        this.db.add_combos(loadedData["pos.combo"]);
        this.db.add_combo_lines(loadedData["pos.combo.line"]);
        //this._loadProductProduct(loadedData["product.product"]);
        this.db.add_packagings(loadedData["product.packaging"]);
        this.attributes_by_ptal_id = loadedData["attributes_by_ptal_id"];
        this._add_ptal_ids_by_ptav_id(this.attributes_by_ptal_id);
        this.cash_rounding = loadedData["account.cash.rounding"];
        this.payment_methods = loadedData["pos.payment.method"];
        this._loadPosPaymentMethod();
        this.fiscal_positions = loadedData["account.fiscal.position"];
        this.base_url = loadedData["base_url"];
        this.pos_has_valid_product = loadedData["pos_has_valid_product"];
        this.db.addProductIdsToNotDisplay(loadedData["pos_special_products_ids"]);
        this.partner_commercial_fields = loadedData["partner_commercial_fields"];
        this.show_product_images = loadedData["show_product_images"] === "yes";
        this.show_category_images = loadedData["show_category_images"] === "yes";
        await this._loadPosPrinters(loadedData["pos.printer"]);
        this.open_orders_json = loadedData["open_orders"];
        console.log(loadedData["product.product"]);
        console.log(loadedData["product.template"]);
        this._loadProductProduct(loadedData["product.template"]);
    },
    _loadProductProduct(products) {
        if (!products || !Array.isArray(products)) {
            console.error('Invalid products data:', products);
            return;
        }

        const productMap = {};
        const productTemplateMap = {};

        const modelProducts = products.map((product) => {
            product.pos = this;
            product.env = this.env;
            product.applicablePricelistItems = {};
            productMap[product.product_variant_id] = product;

            const templateId = product.product_variant_id[0];
            if (!productTemplateMap[templateId]) {
                productTemplateMap[templateId] = [];
            }
            productTemplateMap[templateId].push(product);

            return new Product(product);
        }).filter(product => product !== null);
        for (const pricelist of this.pricelists) {
            console.log("Start");
            for (const pricelistItem of pricelist.items) {
            console.log(pricelistItem);
                if (pricelistItem.product_id) {
                    // Handle pricelist items assigned to specific products
                    const product_id = pricelistItem.product_id[0];
                    const correspondingProduct = productMap[product_id];
                    if (correspondingProduct) {
                        // Ensure final price is used
                        const finalPrice = correspondingProduct.list_price;
                        this._assignApplicableItems(pricelist, correspondingProduct, pricelistItem, finalPrice);
                    }
                } else if (pricelistItem.product_variant_id) {
                    // Handle pricelist items assigned to specific product variants
                    const product_variant_id = pricelistItem.product_variant_id[0];
                    const correspondingProducts = productTemplateMap[product_variant_id];
                    if (correspondingProducts) {
                        for (const correspondingProduct of correspondingProducts) {
                            // Ensure final price is used
                            const finalPrice = correspondingProduct.list_price;
                            this._assignApplicableItems(finalPrice, correspondingProduct, pricelistItem);
                        }
                    }
                } else {
                    // Handle pricelist items that apply to all products
                    for (const correspondingProduct of products) {
                        // Ensure final price is used
                        const finalPrice = correspondingProduct.list_price;
                        this._assignApplicableItems(finalPrice, correspondingProduct, pricelistItem);
                    }
                }
            }
        }
        this.db.add_products(modelProducts);
    },
    async getProductInfo(product, quantity) {
        const order = this.get_order();
        // check back-end method `get_product_info_pos` to see what it returns
        // We do this so it's easier to override the value returned and use it in the component template later
        const productInfo = await this.orm.call("product.template", "get_product_info_pos", [
            [product.id],
            product.get_price(order.pricelist, quantity),
            quantity,
            this.config.id,
        ]);
        productInfo.optional_products = productInfo.optional_products || [];

        const priceWithoutTax = productInfo["all_prices"]["price_without_tax"];
        const margin = priceWithoutTax - product.standard_price;
        const orderPriceWithoutTax = order.get_total_without_tax();
        const orderCost = order.get_total_cost();
        const orderMargin = orderPriceWithoutTax - orderCost;

        const costCurrency = this.env.utils.formatCurrency(product.standard_price);
        const marginCurrency = this.env.utils.formatCurrency(margin);
        const marginPercent = priceWithoutTax
            ? Math.round((margin / priceWithoutTax) * 10000) / 100
            : 0;
        const orderPriceWithoutTaxCurrency = this.env.utils.formatCurrency(orderPriceWithoutTax);
        const orderCostCurrency = this.env.utils.formatCurrency(orderCost);
        const orderMarginCurrency = this.env.utils.formatCurrency(orderMargin);
        const orderMarginPercent = orderPriceWithoutTax
            ? Math.round((orderMargin / orderPriceWithoutTax) * 10000) / 100
            : 0;
        return {
            costCurrency,
            marginCurrency,
            marginPercent,
            orderPriceWithoutTaxCurrency,
            orderCostCurrency,
            orderMarginCurrency,
            orderMarginPercent,
            productInfo,
        };
    }
});
