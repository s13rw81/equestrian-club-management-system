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
   "location": {
      "lat": "latitude",
      "long": "longitude"
   },
   "driver": {
      "name": "name of the driver",
      "phone_no": "phone no of the driver"
   }
   "name": "the name of the truck"
}
```
#### Request Validations
1. The `logistic_company` associated with the `user` must have been verified by the khayyal-admin. That means
   `logistic_company.is_khayyal_verified` must be `true`.
2. A `truck` with the same registration number must not exist in the database.
3. All the fields are mandatory unless otherwise indicated.
4. For all the `string` type fields, empty string wouldn't be accepted as a valid input.

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
         "location": {
            "lat": "latitude",
            "long": "longitude"
         },
         "driver": {
            "name": "name of the driver",
            "phone_no": "phone no of the driver"
         }
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
   "location": {
      "lat": "latitude",
      "long": "longitude"
   },
   "driver": {
      "name": "name of the driver",
      "phone_no": "phone no of the driver"
   }
   "name": "the name of the truck"
}
```
**Notes**:
1. All the fields are optional in the request body. The provided fields will be updated. 

#### Request Validations
1. The `logistic_company` of the `user` must be the owner of the truck.
2. Same validations will apply as per the `/logistic-company/trucks/add-truck` route.
3. In case the registration number is being updated, a `truck` with the new registration number
   must not exist in the database.
4. For all the `string` type fields, empty string wouldn't be accepted as a valid input.

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
      "location": {
         "lat": "latitude",
         "long": "longitude"
      },
      "driver": {
         "name": "name of the driver",
         "phone_no": "phone_no of the driver"
      },
      "name": "the name of the truck",
      "image_urls": ["image_1", "image_2"]
   }
]
```

**Notes**:

1. Since the query is only from a single collection, usage of `mongodb-aggregation-framework` is
   not necessary. However, you can still choose to use it, it will be easier to extend it down the line.
2. Ensure only the `trucks` associated with the `logistic_company` is returned.
3. The `image_urls` key will contain a list of image urls generated using the
   image handling mechanism. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.

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
   "location": {
      "lat": "latitude",
      "long": "longitude"
   },
   "driver": {
      "name": "the name of the driver",
      "phone_no": "the phone_no of the driver"
   }
   "name": "the name of the truck",
   "image_urls": ["image_1", "image_2"]
}
```

**Notes**:

1. Since the query is only from a single collection, usage of `mongodb-aggregation-framework` is
   not necessary. However, you can still choose to use it, it will be easier to extend it down the line.
2. Ensure the requested `truck` is owned by the `logistic-company`.
3. The `image_urls` key will contain a list of image urls generated using the
   image handling mechanism. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.

## User Logistics

### 1. `/user/logistics/find-nearby-trucks`

The `users` of the consumer app will call this route to find nearby trucks stituated within a specified radius.


#### HTTP Method

`GET`

#### The Process

- When an `user` wants to make a logistic booking he will call this route to get all the nearby trucks within a specified radius.
- The `user` will provide the radius through query parameters. The radius will be in KM.

#### Query Parameters
1. `radius`: The `radius` within which the `user` would like to search for `trucks`. The unit of the `radius` will be `KM`. This query parameter will be of `float` type and optional with a default value of 10.
3. `lat`: The `lat` will be of `float` type and mandatory; indicating the `latitude` of the location centering which the user wants to perform the search.
4. `long`: The `long` will be of `float` type and mandatory; indicating the `longitude` of the location centering which the user wants to perform the search.\

**For example:** If the user wants to locate `trucks` within the radius 5 KM it will send 5 as the radius. As in, `/user/logistics/find-nearby-trucks?radius=5&lat=24.45N&long=45.80E`

#### Authentication and RBAC

1. This will be an `authenticated` route.
2. Only users with `user_role`: `USER` will have the permission
   to access this route.

#### The Flow

1. Query the `trucks` collection to get all the trucks.
2. User the `haversine` formula to determine the distance between the `user` provided location and the location of the `trucks`. Filter out only the `trucks` that fall within the `radius`.
Read more about the `haversine` algorithm: [straight-line distance between two co-ordinates - ChatGPT](https://chatgpt.com/share/748d7116-6ba2-4ef9-82b6-07fcb20e9bac)

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
      "location": {
         "lat": "latitude",
         "long": "longitude"
      },
      "driver": {
         "name": "name of the driver",
         "phone_no": "phone_no of the driver"
      }
      "name": "the name of the truck",
      "image_urls": ["image_1", "image_2"]
   }
]
```

**Notes**:

1. Ensure only the `trucks` associated with the `logistic_company` is returned.
2. The `image_urls` key will contain a list of image urls generated using the
   image handling mechanism. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.

#### Pagination:

This route will need `pagination` and `filtering`. Don't worry about
it until the codebase wide `pagination-system` is implemented.

### 2. `/user/logistics/create-booking`

A `user` from the consuemer app will call this route to create a `logistic-booking`. 

#### HTTP Method
`POST`

#### The Process
1. The `user` will call this route from the consumer app to create a `logistic-booking`.

#### Request Body
```json
{
   "truck_id": "id of the truck of the client's choice",
   "pickup": {
      "lat": "the latitude of the pickup location",
      "long": "the longitude of the pickup location"
   },
   "destination": {
      "lat": "the latitude of the destination location",
      "long": "the longitude of the destination locatoin"
   },
   "groomer": {
      "name": "name of the groomer",
      "phone_no": "phone_no of the groomer"
   },
   "details": "details of the consignment"
}
```
#### Request Validations
1. For all the `string` type fields, empty string wouldn't be accepted as a valid input.
2. The `truck_id` must be a valid `truck_id`.

**Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC
1. This will be an `authenticated` route.
2. Only users with `user_role`: `USER` will have the permission to acess this route.

#### The Flow:
1. Find out the `logistic_company` that owns the `truck` associated with the `truck_id` provided in the request.
1. A new document will be created in the `logistic_service_booking` collection.
The schema of the document will be similar to the following:
      ```json
      {
         "_id": ObjectId("12345"),
         "logistics_company_id": "the id of the logistic_company what owns the provided truck",
         "truck_id": "id of the truck of the client's choice",
         "consumer": {
            "consumer_id": "the id of the user who's making the booking",
            "consumer_type": "user.roleType, USER as of now"
         }
         "pickup": {
            "lat": "the latitude of the pickup location",
            "long": "the longitude of the pickup location"
         },
         "destination": {
            "lat": "the latitude of the destination location",
            "long": "the longitude of the destination locatoin"
         },
         "groomer": {
            "name": "name of the groomer",
            "phone_no": "phone_no of the groomer"
         },
         "details": "details of the consignment"
      }
      ```

#### Error Handling:
Raise a `HTTPException` if anything goes wrong.

#### The Response:
On success of the prescribed operations return the `_id` of the newly created `logistic_service_booking`.

```json
  {
    "logistic_service_booking": "id of the newly created booking"
  }
```

### 3. `/user/logistics/update-booking/{logistics_service_booking_id}`

A `user` from the consumer will use this route to update a `logistic-service-booking` that he's created.

#### HTTP Method
`PUT`

#### The Process
1. The `user` will use this route to update a `logistic-service-booking` that is created by him.

#### Path Parameters
1. `logistics_service_booking_id`: The `_id` of the `logistic_service_booking` the user wants to update.

#### Request Body
```json
{
   "truck_id": "id of the truck of the client's choice",
   "pickup": {
      "lat": "the latitude of the pickup location",
      "long": "the longitude of the pickup location"
   },
   "destination": {
      "lat": "the latitude of the destination location",
      "long": "the longitude of the destination locatoin"
   },
   "groomer": {
      "name": "name of the groomer",
      "phone_no": "phone_no of the groomer"
   },
   "details": "details of the consignment"
}
```
#### Request Validations
1. All the fields would be optional. Only provided fields will be updated.
2. The `logistics_service_booking_id` must be valid. The `consumer.consumer_id` must match with the `user._id` of the `user` who's making the call. That means the `user` who's doing the update must be the same who created the booking.
3. Request validations of the `/user/logistics/create-booking` route would apply in this route too.
4. For all the `string` type fields, empty string wouldn't be accepted as a valid input.
5. If `truck_id` is provided the new `truck_id` must be associated with the same `logistic_company` as the previous `truck_id`. That means, the `user` won't be able to update the `logistic_company` of the booking.
6.  

**Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC
1. This will be an `authenticated` route.
2. Only users with `user_role`: `USER` will have the permission to acess this route.

#### The Flow:
1. Find the `logistic_service_booking` with the provided `logistics_company_id` in the path parameter.
2. Update all the corresponding fields in the database as provided in the request body.

#### Error Handling:
Raise a `HTTPException` if anything goes wrong.

#### The Response:
On success of the prescribed operations return a generic response.

```json
  {
    "status": "OK"
  }
```

### 4. `/user/logistics/get-booking`

This route will be used by different type of users depending on the situation to get details about the `logistic-service-booking`.

#### HTTP Method

`GET`

#### The Process
1. A `USER` will call this route from the consumer app to get all the `logistic-service-booking` that is made by him.
2. A `LOGISTIC_COMPANY` will use this route from the admin app to get all the `logistic-service-booking` that are made agianst that company.

#### Authentication and RBAC

1. This will be an `authenticated` route.
2. Only users with `user_role`: `USER` and `user_role`: `LOGISTIC_COMPANY` will have the permission
   to access this route.

#### The Flow

1. If the caller is a `USER` find all the `logistic_service_booking` that are made by the user. That means the `logistic_service_booking.consumer.consumer_id` will match with the `user._id`.  
2. If the caller is a `LOGISTIC_COMPANY` find all the `logistic_service_booking` that are made against the `logistic_company`. That means the `logistic_service_booking.logistics_company_id` will match with `logistic_company._id`.

#### Exception Handling:

Raise a `HTTPException` if anything goes wrong.

#### The Response:

On completion of all the operations, return a list of all the data with a similar schema
as the following.

```json
[
   {
      "_id": ObjectId("12345"),
      "logistics_company_id": "logistic_service_booking.logistics_company_id",
      "truck_id": "logistic_service_booking.truck_id",
      "consumer": {
         "consumer_id": "logistic_service_booking.consumer.consumer_id",
         "consumer_type": "logistic_service_booking.consumer.consumer_type"
      }
      "pickup": {
         "lat": "logistic_service_booking.pickup.lat",
         "long": "logistic_service_booking.pickup.long"
      },
      "destination": {
         "lat": "logistic_service_booking.destination.lat",
         "long": "logistic_service_booking.destination.long"
      },
      "groomer": {
         "name": "logistic_service_booking.groomer.name",
         "phone_no": "logistic_service_booking.groomer.phone_no"
      },
      "details": "logistic_service_booking.details"
   }
]
```


#### Pagination:

This route will need `pagination` and `filtering`. Don't worry about
it until the codebase wide `pagination-system` is implemented.

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
   "trucks": ["truck._id", "truck._id"],
   "features": "it will be a string for now, can be a list later",
   "description": "a description of the club-to-club service"
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
1. A new document will be created in the `logistic_service_club_to_club` collection.
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
   "trucks": ["truck._id", "truck._id"],
   "features": "it will be a string for now, can be a list later",
   "description": "a description of the club-to-club service"
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



