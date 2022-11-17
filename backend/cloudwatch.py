import boto3

class CloudWatch:
    watchClient = None

    def __init__(self):
        self.watchClient = boto3.client(
            'cloudwatch',
            region_name = 'us-east-1'
        )
    
    def put_miss_rate(self, instanceID, missRate):
        response = self.watchClient.put_metric_data(
            MetricData = [{
                'MetricName':'MissRate',
                'Dimensions':[{
                    'Name' : 'Instance ID',
                    'Value': instanceID,
                }],
                'Unit':'Percent',
                'Value':missRate
            }],
            Namespace = 'ece1779/a2'
        )
        return response
    
    def put_hit_rate(self, instanceID, hitRate):
        response = self.watchClient.put_metric_data(
            MetricData = [{
                'MetricName':'HitRate',
                'Dimensions':[{
                    'Name':'Instance ID',
                    'Value':instanceID,
                }],
                'Unit':'Percent',
                'Value':hitRate
            }],
            Namespace = 'ece1779/a2'
        )
        return response
    
    def put_number_of_item_in_cache(self, instanceID, number):
        response = self.watchClient.put_metric_data(
            MetricData = [{
                'MetricName':'NumberOfItem',
                'Dimensions':[{
                    'Name':'Instance ID',
                    'Value': instanceID
                }],
                'Unit':'Count',
                'Value':number
            }],
            Namespace = 'ece1779/a2'
        )
        return response
    
    def put_total_size_of_item(self, instanceID, totalSize):
        response = self.watchClient.put_metric_data(
            MetricData = [{
                'MetricName':'TotalSize',
                'Dimensions':[{
                    'Name':'Instance ID',
                    'Value':instanceID
                }],
                'Unit':'Bytes',
                'Value':totalSize
            }],
            Namespace = 'ece1779/a2'
        )
        return response

    def put_number_of_requests(self, instanceID, number):
        response = self.watchClient.put_metric_data(
            MetricData = [{
                'MetricName':"NumberOfRequest",
                'Dimensions':[{
                    'Name':'Instance ID',
                    'Value':instanceID
                }],
                'Unit':'Count',
                'Value':number
            }],
            Namespace = 'ece1779/a2'
        )
        return response
    