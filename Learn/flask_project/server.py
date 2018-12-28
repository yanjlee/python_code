import flask
import os

app=flask.Flask(__name__)


# @app.route("/")
# def index():
#     try:
#         f=open("index.html","rb")
#         data=f.read()
#         f.close()
#         return data
#
#     except Exception as err:
#         return str(err)

# def index():
#     p = flask.request.args.get('province')
#     c = flask.request.args.get('city')
#     print(p,c)
#     return(p+', '+c)
    # try:
    #     province=flask.request.args.get("province") if "province" in flask.request.args else ""
    #     city = flask.request.args.get("city") if "city" in flask.request.args else ""
    #     return(province+","+city)
    # except Exception as err:
    #     return str(err)

# @app.route("/",methods =["GET","POST"])
# def index():
#     try:
#         # # GET
#         # province=flask.request.args.get("province") if "province" in flask.request.args else ""
#         # city = flask.request.args.get("city") if "city" in flask.request.args else ""
#         # # POST
#         # note = flask.request.form.get("note") if "note" in flask.request.form else ""
#
#         # 混合
#         province=flask.request.values.get("province") if "province" in flask.request.values else ""
#         city = flask.request.values.get("city") if "city" in flask.request.values else ""
#         note = flask.request.values.get("note") if "note" in flask.request.values else ""
#
#         return(province+", "+city + '\n' + note)
#     except Exception as err:
#         return(str(err))

# ## 下载文件
# @app.route("/")
# def index():
#     if 'fileName' not in flask.request.values:
#         return('cover.jpg')
#     else:
#         data = b""
#         try:
#             fileName = flask.request.values.get("fileName")
#             if fileName != "" and os.path.exists(fileName):
#                 f = open(fileName, "rb")
#                 data = f.read()
#                 f.close()
#         except Exception as err:
#             data = str(err).encode()
#     return(data)

## 上传文件
@app.route("/upload",methods=["POST"])
def uploadFile():
    msg=""
    try:
        if "fileName" in flask.request.values:
            fileName = flask.request.values.get("fileName")
            data=flask.request.get_data()
            fobj=open("upload "+fileName,"wb")
            fobj.write(data)
            fobj.close()
            msg="OK"
        else:
            msg="没有按要求上传文件"
    except Exception as err:
        print(err)
        msg=str(err)
    return(msg)



if __name__=="__main__":
    app.run()