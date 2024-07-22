# Onboarding API

This set of apis will be used to onboard different types of entities
primarily from the admin app after creation of the user. This includes,
- logistic-company
- club
- trainer

## Logistic Company

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
2. The `email_address` must be a valid email address
4. The user's `otp_verified` must be `true`
5. Any fields shouldn't be an empty string

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

## Club

### 1. `onboarding/create-club`
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
  "name": "name of the club",
  "description": "a description of the club"
  "location": {
    "lat": "latitude",
    "long": "longitude"
  },
  "riding_lesson_service": {
    "pricing_options": [
      {
        "price": 400,
        "number_of_lessons": 10
      }
    ]
  },
  "horse_shoeing_service": {
    "pricing_options": [
      {
        "price": 400,
        "number_of_horses": 10
      }
    ]
  },
  "generic_activity_service": {
    "price": 500
  }
}
```

#### Request Validations
1. A `club` with the same `email_address` must not exist
2. The `email_address` must be a valid email address
3. The user's `otp_verified` must be `true`
4. None of a fields should be an empty string
5. The following are the mandatory fields: `email_address`, `address`, `phone_no`, `name`, `description` and `location`
6. The fields `riding_lesson_service`, `horse_shoeing_service` and `generic_activity_service` are generally optional. However,
   if these are provided, all the nested fields are mandatory.  

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
      "location": {
        "lat": "latitude",
        "long": "longitude"
      },
      "is_khayyal_verified": false,
      "users": [
        {"user_id": "the id of the user"}
      ]
    }
    ```
2. The role of the user would be updated to `UserRoles.CLUB`
3. If `riding_lesson_service` is provided a new document will be created in the
   `riding_lesson_service` collection.
   The schema of the document will be similar to the following:

    ```json
    {
      "_id": ObjectId("12345"),
      "provider": {
        "provider_id": "newly created club_id",
        "provider_type": "CLUB" // this will be the UserRoles enum, in this case it will be UserRoles.CLUB
      },
      "pricing_options": [
        {
          "price": 400,
          "number_of_lessons": 10
        }
      ]
    }
    ```
4. If `horse_shoeing_service` is provided a new document will be created in the
   `horse_shoeing_service` collection.
   The schema of the document will be similar to the following:

    ```json
    {
      "_id": ObjectId("12345"),
      "provider": {
        "provider_id": "newly created club_id",
        "provider_type": "CLUB" // this will be the UserRoles enum, in this case it will be UserRoles.CLUB
      },
      "pricing_options": [
        {
          "price": 400,
          "number_of_horses": 10
        }
      ]
    }
    ```
5. If `generic_activity_service` is provided a new document will be created in the
   `generic_activity_service` collection.
   The schema of the document will be similar to the following:

    ```json
    {
      "_id": ObjectId("12345"),
      "provider": {
        "provider_id": "newly created club_id",
        "provider_type": "CLUB" // this will be the UserRoles enum, in this case it will be UserRoles.CLUB
      },
      "price": 400
    }
    ```

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

### 2. `onboarding/club/upload-images`

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

### 3. `onboarding/get-club`

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


## Trainer

### 1. `onboarding/create-trainer`
Once the user is created using the `auth` apis, the user 
will call this api to onboard itself as a `trainer`.

#### HTTP Method
`POST`

#### The Process
- the user signs up using the `users/signup` route
- the newly created user, in turn, calls the `auth/generate-signup-otp` route
- the user verifies the otp using the `auth/verify-signup-otp` route
- the user calls the `onboarding/create-trainer` route to onboard itself as a `trainer`

#### Request Body

```json
{
  "full_name": "full name of the trainer",
  "email_address": "trainer_name@domain.com",
  "phone_no": "+911111111111",
  "years_of_experience": 3,
  "specializations": "it will be a list of string",
  "training_location" : "it will be a string",
  "available_services": "a list of string",
  "availavility": "TFTTFFT",
  "preferred_time_slots": "TFT",
  "social_media_links": {
    "website": "https://trainer-name.com",
    "linkedin": "https://linkedin.com/trainer-name",
    "instagram": "https://instagram.com/trainer-name",
    "facebook": "https://facebook.com/trainer-name",
    "twitter": "https://twitter.com/trainer-name"
  },
  "biography": "a maximum 100 words string",
  "expertise": "a list of string",
  "levels_taught": "a list of string",
  "club_id": "the id of the club the trainer is affiliated with"
}
```

**Notes**:
1. `availability` would be a 7 character string. The value of each of the
characters would either be `T` or `F`. Each character indicates the availability of the
trainer in the particular weekday starting from `Monday`

**Example**:
If a trainer is only available on Mondays, 
Wednesdays, Thursdays and Sundays the string would be `TFTTFFT`.

2. Similar to 'availability`, `preferred_time_slots` would be a 3 character string.
The value of each of the characters would either be `T` or `F'.
There are three time_slots, namely: `morning`, `afternoon` and `evening`.

**Example**:
If a trainer prefers the `morning` and the `evening` slots the string would be `TFT`.

3. `years_of_experience` would be an `int`.

#### Request Validations
1. A `trainer` with the same `email_address` must not exist.
2. The provided `email_address` should be a valid email address.
3. The user's `otp_verified` must be `true`.
4. None of the fields should be an empty string.
5. Leaving `full_name`, and `email_address` everything else is `optional`.
6. In case `social_media_links` is there in the request body, it must at least provide one link.
In other words, `social_media_links`, if provided, should not be an empty object.
8. All the fields in the `social_media_links` object are `optional`.
However, any one link must be present in case `social_media_links` is there in the request body.
10. Social Media Links:
  i. `website` should be a valid website url
  ii. `linkedin` should be a valid `linkedin` url
  iii. `instagram` should be a valid `instagram` url
  iv. `facebook` should be a valid `facebook` url
  v. `twitter` should be a valid `twitter` url
11. A maximum of 100 words would be allowed in the `biography` field.
12. For all the fields which are of type list of strings, each of the strings inside the lists shouldn't be an empty string.
13. The `club_id` must be valid. In other words, the provided `club_id` should match with any `club._id` in the database. 

**Note**: Use `pydantic` validators for the validations

#### Authentication and RBAC
1. This would be an authenticated route
2. The user must have the role `UserRoles.USER`

#### The Flow
1. A new document will be created in the `trainer` collection.
The schema of the document will be similar to the following:
    ```json
    {
      "_id": ObjectId("12345"),
      "full_name": "full name of the trainer",
      "email_address": "trainer_name@domain.com",
      "phone_no": "+911111111111",
      "years_of_experience": 3,
      "specializations": ["specialization_1", "specialization_2"],
      "training_location" : "Riyadh, Saudi Arabia",
      "available_services": ["service_1", "service_2"],
      "availavility": "TFTTFFT",
      "preferred_time_slots": "TFT",
      "social_media_links": {
        "website": "https://trainer-name.com",
        "linkedin": "https://linkedin.com/trainer-name",
        "instagram": "https://instagram.com/trainer-name",
        "facebook": "https://facebook.com/trainer-name",
        "twitter": "https://twitter.com/trainer-name"
      },
      "biography": "a maximum 100 words string",
      "expertise": ["expertise_1", "expertise_2"],
      "levels_taught": ["level_1", "level_2"],
      "club_id": "the id of the club the trainer is affiliated with",
      "user_id": "the id of the user"
    }
    ```
2. The role of the user would be updated to `UserRoles.TRAINER`

**Note**: Use transactions for the database operations. **(Ignore this requirement until transaction management system is implemented.)**

#### Error Handling

Raise a `HTTPException` if anything goes wrong.

#### The Response

If all the validations pass the request would also succeed. If anything
else goes wrong the pipeline exception handler would catch the error.

Typically, the request would succeed and return,

```json
{"trainer_id":  "the id of the newly created trainer"}
```

### 2. `onboarding/update-trainer`

After onboarding itself as a `trainer` the user may use this route to update the details about
himself.

#### HTTP Method
`PUT`

#### The Process
- The user will onboard itself as a trainer using the `onboarding/create-trainer` route.
- The may use this route to update the details about himself.

#### Request Body

```json
{
  "full_name": "full name of the trainer",
  "email_address": "trainer_name@domain.com",
  "phone_no": "+911111111111",
  "years_of_experience": 3,
  "specializations": "it will be a list of string",
  "training_location" : "it will be a string",
  "available_services": "a list of string",
  "availavility": "TFTTFFT",
  "preferred_time_slots": "TFT",
  "social_media_links": {
    "website": "https://trainer-name.com",
    "linkedin": "https://linkedin.com/trainer-name",
    "instagram": "https://instagram.com/trainer-name",
    "facebook": "https://facebook.com/trainer-name",
    "twitter": "https://twitter.com/trainer-name"
  },
  "biography": "a maximum 100 words string",
  "expertise": "a list of string",
  "levels_taught": "a list of string",
  "club_id": "the id of the club the trainer is affiliated with"
}
```
**Note**: For explanation about the fields please see `onboarding/create-trainer` route.

#### Request Validations
1. Same validations would apply as specified in the `onboarding/create-trainer` route.

**Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC
1. This will be an authentication route
2. The user must have the role `UserRoles.TRAINER'

#### The Flow
1. Update the respective document in the `trainer` collection.
2. In case, the field that is being update is a `list` completely replace the previously stored items.\
  **To Illustrate**:
  The field `specializations` is a `list` of `string`. Let's say it's stored in the database 
  in the following way,
  
    ```json
    {
      "specializations": ["horse riding", "show jumping"]
    }
    ```
    Now, the user, in the request body of this route, sends the following,

    ```json
    {
      "specializations": ["shoeing", "grooming"]
    }
    ```
    In this scenerio, remove the old list entirely and replace it with the newly provided updated list. After the update,
   the value in the database will look like the following,

    ```json
    {
      "specializations": ["shoeing", "grooming"]
    }
    ```

#### Error Handling
Raise a `HTTPException` if anything goes wrong.

#### The Response
On success of the prescribed operations, return a generic response.

```json
{
  "status": "OK"
}
```

### 3. `/onboarding/trainer/upload-certifications`

After onboarding as a `trainer`, the user will use this route to upload certifications.

#### HTTP Method

`POST`

#### The Process

1. The user will provide a list of `files` to be uploaded and associated with the `trainer`.

#### Request Body

The request body would consist of a `list` of files. The files can either be an image or a pdf. You can request files by
creating the route in the following way:

```python
@upload_images_demo_router.post("/onboarding/trainer/upload-certifications")
async def upload_image_demo(images: list[UploadFile]):
```

**Notes**:

1. Check out [upload_images_demo_crud.py](../api/upload_images_demo/upload_images_demo_crud.py)
   file for examples on how to handle image uploads.
2. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.
3. Use the same image handling mechanism for the `pdf` files as well.


#### Authentication and RBAC

1. This route will be an `authenticated` route
2. Only users with `user_role`: `TRAINER` will have the permission to
   access this route.

#### The Flow

1. The files provided by the user will be saved using the `save_image()` function of
   the image handling mechanism.
2. The `image_id`s returned by the image handling mechanism would be saved in the same
   `trainer` collection in the document associated with the `trainer` of the user.
   The `trainer` will be figured out based on the user who calls the route.
   
   The key for saving the certifications would be `certifications`.
    ```json
    {
      "_id": ObjectId("12345"),
      "certifications": ["image_id_1", "image_id_2"]
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

### 4. `/onboarding/trainer/upload-profile-files`

After onboarding as a `trainer`, the user will use this route to upload profile files.

#### HTTP Method

`POST`

#### The Process

1. The user will provide a list of `files` to be uploaded and associated with the `trainer`.

#### Request Body

The request body would consist of a `list` of files. The files can either be an image or a pdf. You can request files by
creating the route in the following way:

```python
@upload_images_demo_router.post("/onboarding/trainer/upload-profile-files")
async def upload_image_demo(images: list[UploadFile]):
```

**Notes**:

1. Check out [upload_images_demo_crud.py](../api/upload_images_demo/upload_images_demo_crud.py)
   file for examples on how to handle image uploads.
2. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.
3. Use the same image handling mechanism for the `pdf` files as well.


#### Authentication and RBAC

1. This route will be an `authenticated` route
2. Only users with `user_role`: `TRAINER` will have the permission to
   access this route.

#### The Flow

1. The files provided by the user will be saved using the `save_image()` function of
   the image handling mechanism.
2. The `image_id`s returned by the image handling mechanism would be saved in the same
   `trainer` collection in the document associated with the `trainer` of the user.
   The `trainer` will be figured out based on the user who calls the route.
   
   The key for saving the profile files would be `profile_files`.
    ```json
    {
      "_id": ObjectId("12345"),
      "profile_files": ["image_id_1", "image_id_2"]
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

### 5. `/onboarding/trainer/upload-profile-picture`

After onboarding as a `trainer`, the user will use this route to upload profile picture.

#### HTTP Method

`POST`

#### The Process

1. The user will provide an image to be uploaded and associated with the `trainer`.

#### Request Body

The request body would consist of an image file. You can request a single image file by
creating the route in the following way:

```python
@upload_images_demo_router.post("/onboarding/trainer/upload-profile-picture")
async def upload_image_demo(images: UploadFile):
```

**Notes**:

1. Check out [upload_images_demo_crud.py](../api/upload_images_demo/upload_images_demo_crud.py)
   file for examples on how to handle image uploads.
2. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.


#### Authentication and RBAC

1. This route will be an `authenticated` route
2. Only users with `user_role`: `TRAINER` will have the permission to
   access this route.

#### The Flow

1. The image file provided by the user will be saved using the `save_image()` function of
   the image handling mechanism.
2. The `image_id` returned by the image handling mechanism would be saved in the same
   `trainer` collection in the document associated with the `trainer` of the user.
   The `trainer` will be figured out based on the user who calls the route.
   
   The key for saving the profile picture would be `profile_picture`.
    ```json
    {
      "_id": ObjectId("12345"),
      "profile_picture": "image_id"
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

#### 6. `/onboarding/get-trainer`

After the user onboards himself as a `trainer`, he calls this route to get details about the `trainer` data associated with him.

#### HTTP Method
`GET`

#### The Process
1. The user onboards himself as a `trainer`.
2. After the successful onboarding, the user calls this route to get details about the `trainer`
   associated with him.

#### Authentication and RBAC
1. This will be an authenticated route.
2. Only users with `user_role`: `TRAINER` will have access to this route.

#### The Flow
1. The user will call this route.
2. This route will return the `trainer` associated with the user.

#### Error Handling
Raise a `HTTPException` if anything goes wrong.

#### The Response
If everything goes well, return a response with a schema similar to the follwing,

```json
{
  "full_name": "john doe",
  "email_address": "trainer_name@domain.com",
  "phone_no": "+911111111111",
  "years_of_experience": 3,
  "specializations": ["specialization_1", "specialization_2"],
  "training_location" : "Riyadh, Saudi Arabia",
  "available_services": ["service_1", "service_2"],
  "availavility": "TFTTFFT",
  "preferred_time_slots": "TFT",
  "social_media_links": {
    "website": "https://trainer-name.com",
    "linkedin": "https://linkedin.com/trainer-name",
    "instagram": "https://instagram.com/trainer-name",
    "facebook": "https://facebook.com/trainer-name",
    "twitter": "https://twitter.com/trainer-name"
  },
  "biography": "a maximum 100 words string",
  "expertise": ["expertise_1", "expertise_2"],
  "levels_taught": ["level_1", "level_2"],
  "club_id": "the id of the club the trainer is affiliated with",
  "certification_urls": [
    "trainer.certifications[0]",
    "trainer.certifications[1]"
  ],
  "profile_file_urls": [
    "trainer.profile_files[0]",
    "trainer.profile_files[1]"
  ],
  "profile_picture_url": "trainer.profile_picture"
}
```

**Notes:**
1. The `certification_urls` and `profile_file_urls` keys will contain a list of image urls generated using the
   image handling mechanism. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.
2. The `profile_picture_url` will also contain an image url generated using the image handling mechanism.



