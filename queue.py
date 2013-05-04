class Queue(object):
    def __init__(self,qname):
        super(Queue, self).__init__()
        self.qname = qname
    def put(self,value):
        '''
            入队列默认到
        '''
        pass
    def get(self):
        '''
            出队列
        '''
        pass
    
    def status(self):
        '''
            返回对了状态
            子类自己实现自己的方式
        '''
    
    def clear(self,start=None,end=None):
        '''
        清除队列
        可以指定开始和结束位置
        '''
        pass
    
    def iter(self):
        pass
    
    def is_in_queue(self,value):
        '''
            值在不在队列中
        '''
        pass
    
    def get_queue_name(self):
        return self.qname
    
    def removevalue(self,value):
        pass

class RedisFifoQueue(Queue):
    def __init__(self,qname,max_size=0):
        '''
            max_size : 队列最大允许长度
        '''
        super(Queue, self).__init__()
        self.qname = qname
        self.max_size = max_size
        
    def size(self):
        return queue_redis.llen(self.qname)
    
    def put(self,value):
        '''
            由于是异步操作，该队列不能保证绝对的最大允许长度，但也差不多
        '''
        if self.max_size > 0 and self.size() >= self.max_size:
            return False
        else:
            queue_redis.rpush(self.qname, value)
            return True
        
    def pop(self):
        return queue_redis.lpop(self.qname)
        
    def remove(self,value):
        return queue_redis.lrem(self.qname, value)
    
    def peep(self):
        '''
            返回队首的元素，但不remove
        '''
        _first = queue_redis.lrange(self.qname, 0, 0)
        return _first[0] if _first else None
    
    def locate(self,value):
        '''
            返回该元素在队列中第一次出现的位置，如果未找到，则返回-1
        '''
        elems =  queue_redis.lrange(self.qname, 0, -1)
        loc = -1
        index = -1
        for elem in elems:
            index += 1
            if elem == value:
                loc = index
                break
        return loc
       
    def clear(self):
        queue_redis.delete(self.qname) 
