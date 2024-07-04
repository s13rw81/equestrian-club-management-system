# Logistics API

This set of apis will be used for `logistics`.

## Logistics Trucks

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


### 3. `/logistic-company/trucks/update-truck/{truck_id}`

#### HTTP Method
`PUT`

#### The Process
1. Logistic companies will use this route to update the trucks.

#### Path Parameters
1. `truck_id`: The `_id` of the `truck` that the user wants to update.


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
**Notes**:
1. All the fields are optional in the request body. The provided fields will be updated. 

#### Request Validations
1. The `logistic_company` of the `user` must be the owner of the truck.
2. In case the registration number is being updated, a `truck` with the new registration number
   must not exist in the database.

**Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC
1. This will be an `authenticated` route.
2. Only users with `user_role`: `LOGISTIC_COMPANY` will have the permission to acess this route.

#### The Flow:
1. Update the corresponding `truck` document of `trucks` collection with the newly provided fields.

#### Error Handling:
Raise a `HTTPException` if anything goes wrong.

#### The Response:
On success of the prescribed operations return a generic response.

```json
  {
    "status": "OK"
  }
```

### 4. `/logistic-company/trucks/get-truck`

Users of type `logistic-company` will use this route to get all the `trucks` that are 
uploaded by them.

#### HTTP Method

`GET`

#### The Process

- After the user onboards itself as a `logistic-company`, it will add `trucks`.
- The user will use this route to get the trucks that are added by him.

#### Authentication and RBAC

1. This will be an `authenticated` route.
2. Only users with `user_role`: `LOGISTIC_COMPANY` will have the permission
   to access this route.

#### The Flow

1. First, get the `logistic_company` associated with the user.
2. Find all the `trucks` that the `logistic_company` is owner of.
3. Return all the `trucks`. 


#### Exception Handling:

Raise a `HTTPException` if anything goes wrong.

#### The Response:

On completion of all the operations, return a list of all the data with a similar schema
as the following.

```json
[
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
]
```

**Notes**:

1. Since the query is only from a single collection, usage of `mongodb-aggregation-framework` is
   not necessary. However, you can still choose to use it, it will be easier to extend it down the line.
2. Ensure only the `trucks` associated with the `logistic_company` is returned.

#### Pagination:

This route will need `pagination` and `filtering`. Don't worry about
it until the codebase wide `pagination-system` is implemented.

### 5. `/logistic-company/trucks/get-truck/{truck_id}`

Users of type `logistic-company` will use this route to get a particular truck
that is uploaded by it.

#### HTTP Method

`GET`

#### The Process

- After the user onboards itself as a `logistic-company`, it will add `trucks`.
- The user will use this route to get a particular `truck`.

#### Path Parameter
1. `truck_id`: The `_id` of the truck the `user` wants detail about. 

#### Authentication and RBAC

1. This will be an `authenticated` route.
2. Only users with `user_role`: `LOGISTIC_COMPANY` will have the permission
   to access this route.

#### The Flow

1. First, get the `logistic_company` associated with the user.
2. Return the `truck` associated with the `truck_id` only if the owner of the
   `truck` is the `logistic_company`.


#### Exception Handling:

Raise a `HTTPException` if anything goes wrong.

#### The Response:

Return the `truck` with a schema similar to the following:

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

**Notes**:

1. Since the query is only from a single collection, usage of `mongodb-aggregation-framework` is
   not necessary. However, you can still choose to use it, it will be easier to extend it down the line.
2. Ensure the requested `truck` is owned by the `logistic-company`.

## Logistics Services

### 1. `/logistic-company/services/add-club-to-club-service`

#### HTTP Method
`POST`

#### The Process
1. The user will use the admin app to onboard itself as a `logistic-company`.
2. After getting onboarded as a logistic company, the user will use this route
   to add the `club-to-club` service it offers.

#### Request Body
```json
{
   trucks: ["truck._id", "truck._id"],
   features: "it will be a string for now, can be a list later",
   description: "a description of the club-to-club service"
}
```

**Notes**:
1. The `trucks` key will contain a `list` of `truck_id`s. A `truck_id` is basically an `_id` of a document in
   the `trucks` collection.

#### Request Validations
1. Each of the `trucks` must be owned by the `logistic-company`. 

**Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC
1. This will be an `authenticated` route.
2. Only users with `user_role`: `LOGISTIC_COMPANY` will have the permission to acess this route.

#### The Flow:
1. A new document will be created in the `logistic_service_club
_to_club` collection.
The schema of the document will be similar to the following:
    ```json
    {
      "_id": ObjectId("12345"),
      "trucks": ["truck._id", "truck._id"],
      "features": "it will be a string for now, can be a list later",
      "description": "a description of the club-to-club service",
      "provider": {
         "provider_id": "logistic_company_id",
         "provider_type": "LOGISTIC_COMPANY"
      }
    }
    ```

#### Error Handling:
Raise a `HTTPException` if anything goes wrong.

#### The Response:
On success of the prescribed operations return the `_id` of the newly created truck.

```json
  {
    "logistic_service_club_to_club_id": "the id of the newly added club-to-club service"
  }
```

### 2. `/logistic-company/services/club-to-club-service/upload-images`

After creating a new `club-to-club-service` the user will use this route to upload the
images associated with the `club-to-club-service`.

#### HTTP Method

`POST`

#### The Process

1. The user will provide a list of images to be uploaded
   and associated with the `club-to-club-service`.

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
1. The `logistic-company` must have a `club-to-club-service` in place before it can acess this route to upload images for it.

#### Authentication and RBAC

1. This route will be an `authenticated` route
2. Only users with `user_role`: `LOGISTIC_COMPANY` will have the permission to
   access this route.

#### The Flow

1. The images provided by the user will be saved using the `save_image()` function of
   the image handling mechanism.
2. The `image_id`s returned by the image handling mechanism would be saved in the same
   `logistic_service_club_to_club` collection; in the document associated with the corresponding `logistic-company` of the user.
   
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

### 3. `/logistic-company/services/update-club-to-club-service`

#### HTTP Method
`PUT`

#### The Process
1. Logistic companies will use this route to update the `club-to-club-service`.


#### Request Body
```json
{
   trucks: ["truck._id", "truck._id"],
   features: "it will be a string for now, can be a list later",
   description: "a description of the club-to-club service"
}
```
**Notes**:
1. All the fields are optional in the request body. The provided fields will be updated.
2. The `trucks` key will contain a `list` of `truck_id`s. A `truck_id` is basically an `_id` of a document in
   the `trucks` collection.

#### Request Validations
1. The `logistic_company` of the `user` must be the owner of the `trucks`.

**Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC
1. This will be an `authenticated` route.
2. Only users with `user_role`: `LOGISTIC_COMPANY` will have the permission to acess this route.

#### The Flow:
1. Update the corresponding `logistic_service_club_to_club` document with the newly provided.
2. In case `trucks` is provided replace all the existing `trucks` entirely with the new `trucks`.

#### Error Handling:
Raise a `HTTPException` if anything goes wrong.

#### The Response:
On success of the prescribed operations return a generic response.

```json
  {
    "status": "OK"
  }
```



