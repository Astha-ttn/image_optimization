# # This is a sample Python script.
#
# # Press Shift+F10 to execute it or replace it with your code.
# # Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
#
#
# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

from functools import lru_cache
import config
from pickle import TRUE
from pickletools import optimize
from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
import logging
import os
from PIL import Image
import requests, shutil
from starlette.responses import StreamingResponse


app = FastAPI()

@lru_cache()
def get_settings():
    return config.Settings()

# img_cache = dict()

@app.get("/")
async def gethome():
    return {"Key": "Hello"}


@app.get("/v1/imgTool/{repo_name}/{dimension}/{image_url:path}")
async def resize_image(repo_name: str, dimension: str, image_url: str, settings: config.Settings = Depends(get_settings)):
    logging.basicConfig(filename="imageResize.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')

    # Creating an object
    logger = logging.getLogger()

    # Setting the threshold of logger to DEBUG
    logger.setLevel(logging.INFO)

    path = settings.image_path

    # get the image name from the URL - this will be used for caching with the namespace
    image_file_name_full = image_url.split("/")[-1]
    image_file_name = image_file_name_full.split(".")[0]
    image_file_ext = image_file_name_full.split(".")[1]

    # DEBUG - inputs recieved
    logger.info("URL: " + image_url + ", NS: " + repo_name + ", dimentions: " + dimension)

    # Look up the source image
    # image_url_hash_key=hash(image_url)
    # if image_url_hash_key not in img_cache.keys():
    # get the image from the URL - this will create a local copy of the image for further process
    res = requests.get(image_url, stream=True)
    # check if URL was successful
    if res.status_code == 200:
        # TODO check if the image URL is already present in the cache by the {repo_name}
        # TODO image should be downloaded only if the source URL isn't in the cache

        # download the image from source URL
        with open(os.path.join(path, image_file_name_full), "wb") as f:
            shutil.copyfileobj(res.raw, f)
            # TODO add this image to cache with the Image URL for future use
            logger.info(str(res.status_code) + " :Image Successfully Saved: " + image_file_name_full)
            # img_cache[image_url_hash_key] = f
            # required dimentions
            size = (int(dimension.split(",")[0].lstrip("h")), int(dimension.split(",")[1].lstrip("w")))
            # check if this image is present in cache for the required size.
            # image should be resized only if it is not present in cache
            # FIXME check implementation of AWS cache instead of dist()
            # image_url_size_hash_key = hash(image_url+size)
            # print(image_url_size_hash_key)
            # if image_url_size_hash_key not in img_cache.keys():
            # create an Image object
            im = Image.open(os.path.join(path,image_file_name_full))
            im.thumbnail(size, Image.ANTIALIAS)
            resized_image_name = image_file_name + "_" + str(size[0]) + "_" + str(size[1]) + "." + image_file_ext

            # FIXME the image compression is not happening - this needs to be fixed
            im.save(os.path.join(path,image_file_name_full), optimize=True)  # TODO save this image to cache under {repo_name}

            # else:
            logger.info(str(res.status_code) + " :Image Couldn't be retrieved")
            # FIXME the rendering is not optimzed yet - this needs to be fixed
            return FileResponse(os.path.join(path, resized_image_name))
    else:
        return {'error': 'error occurred'}
