# Logistics API

This set of apis will be used for `logistics`.

### 1. `/logistic-company/trucks/add-truck`

#### HTTP Method
`POST`

#### The Process
1. The user will use the admin app to onboard itself as a `logistic-company`.
2. After getting onboarded as a logistic company, the user will use this route
   to add the `trucks` for the services it offer.

#### Request Body
```json
{
  "registration_number": "reg no",
  "truck_type": "the type of the truck",
  "capacity": "100MT",
  "special_features": "AC",
  "gps_equipped": true,
  "air_conditioning": true,
  "name": "the name of the truck"
}
```
#### Request Validations
1. The `logistic_company` associated with the `user` must have been verified by the khayyal-admin. That means
   `logistic_company.is_khayyal_verified` must be `true`.
2. A `truck` with the same registration number must not exist in the database.

**Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC
1. This will be an `authenticated` route.
2. Only users with `user_role`: `LOGISTIC_COMPANY` will have the permission to acess this route.

#### The Flow:
1. A new document will be created in the `trucks` collection.
The schema of the document will be similar to the following:
    ```json
    {
      "_id": ObjectId("12345"),
      "logistics_company_id": "the id of the associated logistic company",
      "registration_number": "reg no",
      "truck_type": "the type of the truck",
      "capacity": "100MT",
      "special_features": "AC",
      "gps_equipped": true,
      "air_conditioning": true,
      "name": "the name of the truck"
    }
    ```

#### Error Handling:
Raise a `HTTPException` if anything goes wrong.

#### The Response:
On success of the prescribed operations return the `_id` of the newly created truck.

```json
  {
    "truck_id": "the id of the newly added truck"
  }
```

### 2. `/logistic-company/trucks/upload-truck-images/{truck_id}`

After creating a new `truck` the user will use this route to upload the
images associated with the `truck`.

#### HTTP Method

`POST`

#### The Process

1. The user will provide a list of images to be uploaded
   and associated with the `truck`.

#### Path Parameters
1. `truck_id`: This will be the `id` of the `truck` for which the images are being upload. This
   `truck_id` would correspond to `trucks._id` in the database.

#### Request Body

The request body would consist of a `list` of images. You can request images by
creating the route in the following way:

```python
@upload_images_demo_router.post("/logistic-company/trucks/upload-truck-images/{truck_id}")
async def upload_truck_images(truck_id: int, images: list[UploadFile]):
```

**Notes**:

1. Check out [upload_images_demo_crud.py](../api/upload_images_demo/upload_images_demo_crud.py)
   file for examples on how to handle image uploads.
2. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.

#### Request Validations
1. The `truck` associated with the provided `truck_id` in path parameter, must be owned
   by the `logistic_company` of the `user`. That is, the `truck.logistics_company_id` must correspond with the
   `logistic_company._id` associated with the user.

#### Authentication and RBAC

1. This route will be an `authenticated` route
2. Only users with `user_role`: `LOGISTIC_COMPANY` will have the permission to
   access this route.

#### The Flow

1. The images provided by the user will be saved using the `save_image()` function of
   the image handling mechanism.
2. The `image_id`s returned by the image handling mechanism would be saved in the same
   `trucks` collection; in the document associated with the `truck_id` provided by the `user`.
   
   The key for saving the images would be `images`.
    ```json
    {
      "_id": ObjectId("12345"),
      "images": ["image_id_1", "image_id_2"]
    }
    ```

#### Error Handling

Raise a `HTTPException` if anything goes wrong.

#### The Response

If everything goes right, return a generic response informing the user that
everything went well.

```json
{
  "status": "OK"
}
```



