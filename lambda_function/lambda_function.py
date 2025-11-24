import json
import boto3
import os
import requests
from io import BytesIO
from PIL import Image
from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact
from basicsr.utils.download_util import load_file_from_url
# from flask import Flask, request, jsonify
import base64


# app = Flask(__name__)

# @app.route("/enhance", methods=["POST"])
# def enhance_local():
#     print("Hello Python")
#     data = request.get_json()
#     image_url = data.get("imageUrl")

#     result = enhance_image(image_url, "/path/to/model.pth", 4)

#     if not result:
#         return jsonify({"status": False, "message": "Failed"}), 500

#     return jsonify({
#         "status": True,
#         "enhanced": result  # base64 output
#     })


# image_path
def enhance_image(image_url, model, scale):
    """
    Enhances an image using the Real-ESRGAN model.
    """
    try:
        print("Hello image")
        # ----------- New Code ------------------
        print("image_url >>>>", image_url)
        response = requests.get(image_url, timeout=10)
        
        if response.status_code != 200:
            print("Failed to download image")
            return None
        # ------------ New Code -----------------


        # img = Image.open(image_path).convert("RGB")

        # ---------- New Code ----------
        img = Image.open(BytesIO(response.content)).convert("RGB")
        # ---------- New Code ----------

        print("Loading RealESRGAN model...")

        enhancer = RealESRGANer(
            scale=scale,
            model_path=model,
            dni_weight=None,
            model=SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=32, upscale=4, act_type='''relu'''),
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=False,
            gpu_id=None,
        )

        upsampled_img, _ = enhancer.enhance(img, outscale=scale)

        print("upsampled_img >>>>>>>>>>>>",upsampled_img)
        # ------------ New Code ------------- 
        # 4. Convert back to bytes
        buffer = BytesIO()
        upsampled_img.save(buffer, format="JPEG")
        buffer.seek(0)

        return buffer.getvalue()  # raw bytes of enhanced image
        # ------------ New Code ------------- 


        # return upsampled_img
    except Exception as e:
        print(f"Error enhancing image: {e}")
        return None


def lambda_handler(event, context):
    print("lambda handler")
    print("event >>>>>>>>> ",event)
    image_url = event.get("imageUrl")  # url from request body
    model_path = load_file_from_url(
        url='''https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth''', 
        model_dir='''/tmp/realesrgan''', 
        progress=True
    )
    scale = 4
    
    enhanced_bytes = enhance_image(image_url, model_path, scale)

    if enhanced_bytes is None:
        return {"status": False, "message": "Image enhancement failed"}

    # return base64 to API Gateway
    # import base64
    encoded_img = base64.b64encode(enhanced_bytes).decode("utf-8")

    return {
        "status": True,
        "enhancedImage": encoded_img
    }


# if __name__ == "__main__":
#     app.run(port=5001, debug=True)




# def lambda_handler(event, context):
    # """
    # AWS Lambda function to enhance images from S3 using Real-ESRGAN.
    # """
    # s3 = boto3.client("s3")
    
    # # Load the Real-ESRGAN model
    # model_path = load_file_from_url(url='''https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth''', 
    #                                 model_dir='''/tmp/realesrgan''', progress=True)


    # try:
    #     body = json.loads(event.get("body", "{}"))
    #     images = body.get("images", [])
    #     profile_pic = body.get("profilePic")
    #     scale = body.get("scale", 4)
    #     output_bucket = body.get("output", {}).get("bucket")
    #     output_prefix = body.get("output", {}).get("prefix", "")

    #     if not output_bucket:
    #         return {
    #             "statusCode": 400,
    #             "body": json.dumps({"error": "Output bucket not specified."}),
    #         }

    #     results = []
    #     profile_pic_result = {}

    #     # Process main images
    #     for img_data in images:
    #         bucket = img_data.get("bucket")
    #         key = img_data.get("key")
    #         if not bucket or not key:
    #             continue

    #         download_path = f"/tmp/{os.path.basename(key)}"
    #         s3.download_file(bucket, key, download_path)

    #         enhanced_image = enhance_image(download_path, model_path, scale)
    #         if enhanced_image:
    #             output_key = f"{output_prefix}{os.path.splitext(os.path.basename(key))[0]}_x{scale}.jpg"
    #             output_path = f"/tmp/enhanced_{os.path.basename(key)}"
    #             enhanced_image.save(output_path, "JPEG")

    #             s3.upload_file(output_path, output_bucket, output_key)

    #             results.append({
    #                 "inputKey": key,
    #                 "outputKey": output_key,
    #                 "width": enhanced_image.width,
    #                 "height": enhanced_image.height,
    #                 "mime": "image/jpeg",
    #             })

    #     # Process profile picture
    #     if profile_pic:
    #         bucket = profile_pic.get("bucket")
    #         key = profile_pic.get("key")
    #         if bucket and key:
    #             download_path = f"/tmp/{os.path.basename(key)}"
    #             s3.download_file(bucket, key, download_path)

    #             enhanced_image = enhance_image(download_path, model_path, scale)
    #             if enhanced_image:
    #                 output_key = f"{output_prefix}{os.path.splitext(os.path.basename(key))[0]}_x{scale}.jpg"
    #                 output_path = f"/tmp/enhanced_{os.path.basename(key)}"
    #                 enhanced_image.save(output_path, "JPEG")

    #                 s3.upload_file(output_path, output_bucket, output_key)

    #                 profile_pic_result = {
    #                     "inputKey": key,
    #                     "outputKey": output_key,
    #                     "width": enhanced_image.width,
    #                     "height": enhanced_image.height,
    #                     "mime": "image/jpeg",
    #                 }

    #     return {
    #         "statusCode": 200,
    #         "body": json.dumps({
    #             "results": results,
    #             "profilePicResult": profile_pic_result,
    #         }),
    #     }

    # except Exception as e:
    #     print(f"Error: {e}")
    #     return {
    #         "statusCode": 500,
    #         "body": json.dumps({"error": str(e)}),
    #     }