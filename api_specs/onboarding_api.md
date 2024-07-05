# Onboarding API

This set of apis will be used to onboard different types of entities
primarily from the admin app after creation of the user. This includes,
- logistic-company
- club
- trainer

### 1. `onboarding/create-logistic-company`
Once the user is created using the `auth` apis, the user 
will call this api to onboard itself as a `logistic-company`.

#### HTTP Method
`POST`

#### The Process
- the user signs up using the `users/signup` route
- the newly created user, in turn, calls the `auth/generate-signup-otp` route
- the user verifies the otp using the `auth/verify-signup-otp` route
- the user calls the `onboarding/create-logistic-company` route to onboard itself as a `logistic-company`

#### Request Body

```json
{
  "email_address": "someemail@domain.com",
  "phone_no": "+911111111111",
  "name": "name of the logistic-company",
  "description": "a description of the company"
}
```

#### Request Validations
1. A `logistic-company` with the same `email_address` must not exist
2. The user's `otp_verified` must be `true`

**Note**: Use `pydantic` validators for the validations

#### Authentication and RBAC
1. This would be an authenticated route
2. The user must have the role `UserRoles.USER`

#### The Flow
1. A new document will be created in the `logistic_company` collection.
The schema of the document will be similar to the following:
    ```json
    {
      "_id": ObjectId("12345"),
      "email_address": "someemail@domain.com",
      "phone_no": "+911111111111",
      "name": "name of the logistic-company",
      "description": "a description of the company",
      "is_khayyal_verified": false,
      "users": [
        {"user_id": "the id of the user"}
      ]
    }
    ```
2. The role of the user would be updated to `UserRoles.LOGISTIC_COMPANY`

**Note**: Use transactions for the database operations. **(Ignore this requirement until transaction management system is implemented.)**

#### Error Handling

Raise a `HTTPException` if anything goes wrong.

#### The Response

If all the validations pass the request would also succeed. If anything
else goes wrong the pipeline exception handler to catch the error.

Typically, the request would succeed and return,

```json
{"logistic_company_id":  "the id of the newly created logistic_company"}
```

### 2. `onboarding/logistic-company/upload-images`

After onboarding as a `logistic_company`, the user will use this route to upload images
of the `logistic_company`.

#### HTTP Method

`POST`

#### The Process

1. The user will provide a list of images to be uploaded
   and associated with the `logistic_company`.

#### Request Body

The request body would consist of a `list` of images. You can request images by
creating the route in the following way:

```python
@upload_images_demo_router.post("/onboarding/logistic-company/upload-images")
async def upload_image_demo(images: list[UploadFile]):
```

**Notes**:

1. Check out [upload_images_demo_crud.py](../api/upload_images_demo/upload_images_demo_crud.py)
   file for examples on how to handle image uploads.
2. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.


#### Authentication and RBAC

1. This route will be an `authenticated` route
2. Only users with `user_role`: `LOGISTIC_COMPANY` will have the permission to
   access this route.

#### The Flow

1. The images provided by the user will be saved using the `save_image()` function of
   the image handling mechanism.
2. The `image_id`s returned by the image handling mechanism would be saved in the same
   `logistic_company` collection in the document associated with the `logistic_company` of the user.
   The `logistic_company` will be figured out based on the user who calls the route.
   
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

### 3. `onboarding/get-logistic-company`

After the user onboards himself as a `logistic-company`, he calls this route to get details about his `logistic-company`.

#### HTTP Method
`GET`

#### The Process
1. The user onboards himself as a `logistic-company`.
2. After the successful onboarding, the user calls this route to get details about his
   `logistic-company`.

#### Authentication and RBAC
1. This will be an authenticated route.
2. Only users with `user_role`: `LOGISTIC_COMPANY` will have access to this route.

#### The Flow
1. The user will call this route.
2. This route will return the `logistic-company` associated with the user.

#### Error Handling
Raise a `HTTPException` if anything goes wrong.

#### The Response
If everything goes well, return a response with a schema similar to the follwing,

```json
{
  "id": "the id of the logistic_company",
  "email_address": "someemail@domain.com",
  "phone_no": "+911111111111",
  "name": "name of the logistic-company",
  "description": "a description of the company",
  "is_khayyal_verified": false,
  "image_urls": [
    "logistic_companies.images[0]",
    "logistic_companies.images[1]"
  ]
}
```

**Notes:**
1. The `image_urls` key will contain a list of generated image urls using the
   image handling mechanism. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.
   

### 4. `onboarding/create-club`
Once the user is created using the `auth` apis, the user 
will call this api to onboard itself as a `club`.

#### HTTP Method
`POST`

#### The Process
- the user signs up using the `users/signup` route
- the newly created user, in turn, calls the `auth/generate-signup-otp` route
- the user verifies the otp using the `auth/verify-signup-otp` route
- the user calls the `onboarding/create-club` route to onboard itself as a `logistic-company`

#### Request Body

```json
{
  "email_address": "someemail@domain.com",
  "address": "the address of the club",
  "phone_no": "+911111111111",
  "name": "name of the logistic-company",
  "description": "a description of the company"
}
```

#### Request Validations
1. A `club` with the same `email_address` must not exist
2. The user's `otp_verified` must be `true`

**Note**: Use `pydantic` validators for the validations

#### Authentication and RBAC
1. This would be an authenticated route
2. The user must have the role `UserRoles.USER`

#### The Flow
1. A new document will be created in the `club` collection.
The schema of the document will be similar to the following:
    ```json
    {
      "_id": ObjectId("12345"),
      "email_address": "someemail@domain.com",
      "address": "the address of the coub",
      "phone_no": "+911111111111",
      "name": "name of the logistic-company",
      "description": "a description of the company",
      "is_khayyal_verified": false,
      "users": [
        {"user_id": "the id of the user"}
      ]
    }
    ```
2. The role of the user would be updated to `UserRoles.CLUB`

**Note**: Use transactions for the database operations. **(Ignore this requirement until transaction management system is implemented.)**

#### Error Handling

Raise a `HTTPException` if anything goes wrong.

#### The Response

If all the validations pass the request would also succeed. If anything
else goes wrong the pipeline exception handler will catch the error.

Typically, the request would succeed and return,

```json
{"club_id":  "the id of the newly created club"}
```

### 5. `onboarding/club/upload-images`

After onboarding as a `club`, the user will use this route to upload images
of the `club`.

#### HTTP Method

`POST`

#### The Process

1. The user will provide a list of images to be uploaded
   and associated with the `club`.

#### Request Body

The request body would consist of a `list` of images. You can request images by
creating the route in the following way:

```python
@upload_images_demo_router.post("/onboarding/logistic-company/upload-images")
async def upload_image_demo(images: list[UploadFile]):
```

**Notes**:

1. Check out [upload_images_demo_crud.py](../api/upload_images_demo/upload_images_demo_crud.py)
   file for examples on how to handle image uploads.
2. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.


#### Authentication and RBAC

1. This route will be an `authenticated` route
2. Only users with `user_role`: `CLUB` will have the permission to
   access this route.

#### The Flow

1. The images provided by the user will be saved using the `save_image()` function of
   the image handling mechanism.
2. The `image_id`s returned by the image handling mechanism would be saved in the same
   `club` collection in the document associated with the `club` of the user.
   The `club` will be figured out based on the user who calls the route.
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

### 6. `onboarding/get-club`

After the user onboards himself as a `club`, he calls this route to get details about his `club`.

#### HTTP Method
`GET`

#### The Process
1. The user onboards himself as a `club`.
2. After the successful onboarding, the user calls this route to get details about his
   `club`.

#### Authentication and RBAC
1. This will be an authenticated route.
2. Only users with `user_role`: `CLUB` will have access to this route.

#### The Flow
1. The user will call this route.
2. This route will return the `club` associated with the user.

#### Error Handling
Raise a `HTTPException` if anything goes wrong.

#### The Response
If everything goes well, return a response with a schema similar to the follwing,

```json
{
  "id": "the id of the club",
  "email_address": "someemail@domain.com",
  "address": "the address of the club"
  "phone_no": "+911111111111",
  "name": "name of the club",
  "description": "a description of the club",
  "is_khayyal_verified": false,
  "image_urls": [
    "club.images[0]",
    "club.images[1]",
    "club.images[3]"
  ]
}
```

**Notes:**
1. The `image_urls` key will contain a list of generated image urls using the
   image handling mechanism. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.
