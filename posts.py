import zlib as zip

class post:
    def __init__(self,user_id,post_id,time_created,like_count,content):
        self.user = user_id
        self.post_id = post_id
        self.time = time_created
        self.like = like_count
        self.post_liker = []
        self.content = zip.compress(content.encode('utf-8'))

    def add_like(self,liker_id):
        self.like+=1
        self.post_liker.append(liker_id)



