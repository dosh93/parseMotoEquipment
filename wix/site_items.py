class WixItem:

    def __init__(self, name: str, price: int, description: str, product_options: list, variant_options: list, media: list):
        self.product = {
            "product": {
                "name": name,
                "productType": "physical",
                "priceData": {
                    "price": price
                },
                "description": description,
                "sku": "",
                "visible": True,
                "manageVariants": True,
                "productOptions": product_options
            }
        }
        self.variantOptions = variant_options
        self.media = media

    def get_product_wix(self):
        return self.product

    def get_media_wix(self):
        return self.media

    def get_variant_wix(self):
        return self.variantOptions

    def get_product_for_update(self):
        return {
            "product": {
                "name": self.product["product"]["name"],
                "productType": "physical",
                "priceData": {
                    "price": self.product["product"]["priceData"]["price"]
                },
                "sku": "",
                "visible": True,
                "manageVariants": True,
                "productOptions": self.product["product"]["productOptions"]
            }
        }
