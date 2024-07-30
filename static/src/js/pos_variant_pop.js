/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";

export class VariantInfoPopup extends AbstractAwaitablePopup {
    static template = "point_of_sale.VariantInfoPopup";
    static defaultProps = { confirmKey: false };

     setup() {
        super.setup();
        this.pos = usePos();
        Object.assign(this, this.props.info);
    }
    searchProduct(productName) {
        this.pos.setSelectedCategoryId(0);
        this.pos.searchProductWord = productName;
        this.cancel();
    }
}

export class ExtendedProductCard extends ProductCard {
    static template = 'point_of_sale.ProductCardExtension'; // Ensure this matches your template name

    static props = {
        ...ProductCard.props,
        onProductVariantClick: { type: Function, optional: true },
    };

    // Override or add methods
    handleProductVariantClick(event) {
        console.log('Product Variant Clicked'); // Debugging line
        if (this.props.onProductVariantClick) {
            console.log('Calling onProductVariantClick'); // Debugging line
            this.props.onProductVariantClick(event);
        }
    }
}

