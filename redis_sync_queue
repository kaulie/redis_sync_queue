def simple_sync_queue(queue_key_pattern,req_ttl = 0.5, wait_timeout = 2.0,max_size=0,logger=None,queue_ttl = 0,queue_expireat=None):
    '''
        queue_key:请求队列key
        req_ttl: 一个请求在队列中的生存时间,应该比方法执行的时间略大，默认为500毫秒
        wait_timeout: 单个请求的最大等待时间，默认为2秒
        max_size : 队列的最大请求容量，默认为0，即没有限制
        logger : 使用的logger，如果不设置，则使用系统内置logging  
        callback : 失败时的回调函数，默认在请求未满足时，返回一个json串，可以支持自定义
        queue_ttl : 队列的生存周期,如果没有设定，0 为不过期,必须为大于0的int值
        queue_expireat: 队列的绝对过期时间,None为不过期
        queue_ttl 与 queue_expireat 同时存在时，以 queue_expireat 设置为准
    '''
    assert isinstance(queue_ttl,int)
    def deco(method):
        arg_names, varargs, varkw, defaults = inspect.getargspec(method)
        gen_queue_key = __gen_key_factory(queue_key_pattern, arg_names, defaults)
        _logger = logger or logging.getLogger()
        @functools.wraps(method)
        def _(*args, **kwargs):
            #根据key的类型获取redis的存储
            c = get_activitie_redis_client()
            req_time = int(now_second())
            queue_key = gen_queue_key(*args)
            print 'queue_key==========>',queue_key
            queue = RedisFifoQueue(queue_key,max_size=max_size)
            #内置计数器
            queue_counter_key = queue_key+"_counter"
            
            #定义过期策略
            if not c.exists(queue_key):
                if queue_expireat:
                    c.expireat(queue_key, queue_expireat)
                    c.expireat(queue_counter_key, queue_expireat)
                elif queue_ttl:
                    c.expire(queue_key, queue_ttl)
                    c.expire(queue_counter_key, queue_ttl)
                    
            #先取号
            seqnum = c.incr(queue_counter_key, 1)
            #以redis的server时间为准
            redis_time = c.time()
            precision = len(str(redis_time[1])) #精度的位数(毫秒)
            _req = '%s|%s%s' % (str(seqnum),str(redis_time[0]),str(redis_time[1]))
            print '_req==================',_req
            print '======在我前面还有%s个人' % queue.size()
            
            can_execute = False
            if not queue.put(_req):
                print(u'求队列已经达到最大人数')
            else:
                print '成功加入队列'
            while True:
                top_req = queue.peep()
                if not top_req : 
                    can_execute = True
                    break
                else:
                    req_info = top_req.split('|')
                    (_num,_ts) = (int(req_info[0]),req_info[1])
                    if _num == seqnum:
                        can_execute = True
                        break
                    
                    #先检查[防止进程异常造成的请求未及时删除]，再sleep
                    inqueue_ts = float(top_req.split('|')[1]) #入队列的时间
                    redis_time = c.time()
                    now_ts = int('%s%s' % (str(redis_time[0]),str(redis_time[1])))
                    if (now_ts - inqueue_ts) >= req_ttl*(10**precision):
                        #请求长时间未响应，予以删除
                        queue.remove(top_req)
                    else:
                        time.sleep(0.1)
                    
                    if (int(now_second()) - req_time) >= wait_timeout:
                        logging.info(u'请求超时')
                        break
                    
            result = None
            try :
                if can_execute:
                    result  =  method(*args, **kwargs)#执行方法
                else:
                    raise Exception('系统繁忙，请稍后再试')
            except Exception,e :
                logging.info('simple_sync_queue====>except:===>%s' % e)
            finally:  
                queue.remove(_req)
                
            return result
            
        return _
    return deco
