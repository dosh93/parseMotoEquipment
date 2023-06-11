class WixItem:

    def __init__(self, name: str, price: int, description: str, product_options: list, variant_options: list,
                 media: list):
        self.product = {
            "product": {
                "name": name,
                "productType": "physical",
                "priceData": {
                    "price": price
                },
                "description": description[:8000],
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

    def clean_media(self, product_from_wix):
        choices = next((productOption["choices"] for productOption in product_from_wix["product"]["productOptions"] if
                        productOption["name"] == "Цвет"), None)

        color_with_photo = [choice["value"] for choice in choices if "media" in choice]
        self.media['media'] = [one_media for one_media in self.media['media'] if
                               one_media['choice']['choice'] not in color_with_photo]
