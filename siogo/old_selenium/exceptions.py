class ScrapperFail(Exception):
    pass

class TooManyRetries(ScrapperFail):
    pass

class PageNotLoaded(ScrapperFail):
    pass

class NotUserApproved(ScrapperFail):
    pass
