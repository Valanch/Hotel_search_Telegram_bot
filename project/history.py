class History:  # work in progress, will track individual users' logs

    def __init__(self, log_dict, num=0, hotel_num=0, hotels=None, photo_check=0, price_sort="PRICE_LOW_TO_HIGH"):
        self.log = log_dict
        self.num = num
        self.hotel_num = hotel_num
        self.hotels = hotels
        self.photo_check = photo_check
        self.price_sort = price_sort


history = History(log_dict=dict())