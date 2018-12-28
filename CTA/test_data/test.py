from ConnectDB import get_all_data
from datetime import timedelta, datetime
import easytrader

# 登录 easytrader 支持的用户，以 银河证券 为例
ht_user = easytrader.use('ht_client')
ht_user.prepare(user='020400149528', password='661966', comm_password='991699')



