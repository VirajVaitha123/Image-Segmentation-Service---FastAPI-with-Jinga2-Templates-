"""
routing code for clustering_examples usecase in our FastAPI webservice. 

Storing seperate GET/POST request in routers to better organise and prevent clutter in the main.py file.
"""
from internal.data_processing.img_utils import bytes_to_numpy_array, resolution_matcher
from internal.data_processing.azure_blob_wrapper import upload_blob
from internal.machine_learning.image_segmentation import cluster_image
import matplotlib.pyplot as plt

from fastapi import APIRouter
from fastapi import FastAPI, Request, File, Form,UploadFile, Depends, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


from PIL import Image

tags_metadata = [
    {
        "name": "clustering_examples",
        "description": "APIs to showcase unsupervised learning applications",
    }
]



router = APIRouter(
    prefix="/clustering_examples",
    tags=["clustering_examples"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


templates = Jinja2Templates(directory="templates")
router.mount("/static", StaticFiles(directory="static"), name = "static")


@router.get('/', response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("clustering_examples.html",
                                     {"request": request})


@router.post('/submit', response_class=HTMLResponse)
async def post_form(request: Request,k_cluster: int = Form(...), file: UploadFile = File(...)):
    # Read uploaded file as bytes
    data = await file.read()
   
    # Convert Bytes to numpy (great to work with images and processing for machine learning)
    img_array = bytes_to_numpy_array(data, scale = True)
    fig_size = resolution_matcher(img_array,dpi=50)

    
    # Create a figure of the right size with one axes that takes up the full figure
    fig = plt.figure(figsize=fig_size)
    segmented_img = cluster_image(k_cluster,img_array)

    
    plt.imshow(segmented_img,interpolation='nearest')
    # plt.title("new image")

    plt.subplots_adjust(0,0,1,1)
    plt.axis('off')
    filepath = r"C:\Users\viraj.vaitha\FastAPI_Create_your_own_API\figures\segmented_image_{0}.jpg".format(k_cluster)
    plt.savefig(filepath,  dpi=200)

    seg_image = Image.open(filepath)

    filename = file.filename
    upload_blob(filename,"public",filepath)
    return templates.TemplateResponse(r"clustering_examples.html",
                                     {'request': request})