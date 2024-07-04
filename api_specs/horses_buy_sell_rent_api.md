# Horses buy-sell-rent API

This set of apis will be utilized to manage the buy, sell and rent of
the horses. The `users` and `clubs` will enlist horses for others
to buy or rent. As of now, `users` will be able to see the listing and make
enquiry for the listing. The `enquiries` will be accessible by `khayyal-admin`.

### 1. `user/horses/enlist-for-sell`

Users will use this route to enlist new horses that is available for selling.

#### HTTP Method

`POST`

#### The Process

- The user signs up using the `users/signup` route
- The user use this route to enlist a horse for selling
- This route may also be used by a `club`
- The differences between a `user` and a `club` are the following:
    1. firstly, the`user_role` of an `user` is set to `USER`, for a club it's `CLUB`.
    2. Secondly, a `club` has a `club` entity associated with it. The
       corresponding `club` entity can be found from the `club` collection.

#### Request Body

```json
{
  "name": "A name of the horse",
  "year_of_birth": "2069",
  "breed": "top class horse breed",
  "size": "size of the horse",
  "gender": "male",
  "description": "a description of the horse",
  "price": "1000 SAR"
}
```

#### Authentication and RBAC

1. This will be an `authenticated` route.
2. Only users with `user_role`: `CLUB` and `USER` will have the permission
   to access this route.

#### The Flow

1. A new document in the `horses` collection will be created. The schema of
   the document will be similar to the following:

    ```json
    {
          "_id": ObjectId("12345"),
          "name": "A name of the horse",
          "year_of_birth": "2069",
          "breed": "top class horse breed",
          "size": "size of the horse",
          "gender": "male",
          "description": "a description of the horse",
          "uploaded_by": {
            "uploaded_by_id": user_id,
            "uploaded_by_user": "USER" or "CLUB"
          }
    }
    ```
2. Obtain the `horse_id` that was generated in the previous step and create a new
   document in the `horse_selling_service` collection. The schema of the document will
   be similar to the following:

    ```json
      {
        "_id": ObjectId("12345"),
        "horse_id": "the horse_id from the previous step",
        "price": "1000 SAR",
        "provider": {
          "provider_id": "club_id if it's a club otherwise user_id",
          "provider_type": "USER" or "CLUB"
        }    
      }  
    ```

**Note**:

- Use transactions for the database operations. **(Ignore this requirement until transaction management system is
  implemented.)**
- As of now, only `USER` will use this route. So, don't worry about `CLUB` too much.

#### Exception Handling:

Raise a `HTTPException` if anything goes wrong.

#### The Response:

On completion of all the operations, return the `horse_selling_service_id`.

```json
{
  "horse_selling_service_id": "horse_selling_service_id"
}
```

### 2. `user/horses/{horse_selling_service_id}/upload-images`

After enlisting a horse for sale using the `user/horses/enlist-horse-for-sell` route
the user will use this route to upload images of the horse.

#### HTTP Method

`POST`

#### The Process

1. The user will provide a list of images to be uploaded
   and associated with the `horse_selling_service`.

#### Path Parameters

1. `horse_selling_service_id`: This would be the `_id` of the `horse_selling_service`
   . This parameter would match the `horse_selling_service._id` in the database.

#### Request Body

The request body would consist of a `list` of images. You can request images by
creating the route in the following way:

```python
@upload_images_demo_router.post("/user/horses/{horse_selling_service_id}/upload-images")
async def upload_image_demo(horse_selling_service_id: str, image: list[UploadFile]):
```

**Notes**:

1. Check out [upload_images_demo_crud.py](../api/upload_images_demo/upload_images_demo_crud.py)
   file for examples on how to handle image uploads.
2. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.

#### Request Validations

1. The `horse_selling_service_id` provided as a path parameter must have been
   created by the requesting user.

**Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC

1. This route will be an `authenticated` route
2. Only users with `user_role`: `CLUB` and `USER` will have the permission to
   access this route.

#### The Flow

1. The images provided by the user will be saved using the `save_image()` function of
   the image handling mechanism.
2. The `image_id`s returned by the image handling mechanism would be saved in the same
   `horses` collection in the document associated with the `horse_selling_service_id`.
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

### 3. `user/horses/get-horses-for-sell`

Users will use this route to get the horses:
- that are on sale and listed by others
- listed for sale by the user himself

#### HTTP Method

`GET`

#### The Process

- The `user` uses this route for two purposes.
    1. to get all the horses that are listed for sale by others
    2. to get all the horses that were listed by him
- We use a query parameter to figure out whether to send the horses listed by
  others, or the horses listed by him.

#### Query Parameters

1. `own_listing`: the type of this parameter would be of `bool` type. It will be
   an optional parameter with a default value of `false`.

#### Authentication and RBAC

1. This will be an `authenticated` route.
2. Only users with `user_role`: `CLUB` and `USER` will have the permission
   to access this route.

#### The Flow

1. Based on the query parameter it would be decided whether to return the listings
   added the `user` or to return listings added by others.
2. If the query parameter `own_listing=true` return the listings of the user.
   Otherwise, return the listing of others.
3. While returning the listing of others make sure to exclude items that were
   created by the user himself.
5. Query the `horse_selling_service` collection. Use `mongodb aggregate pipeline`
   and `lookup` to join the collection with the `horses` collection. Return the data
   to the user.

**Notes**:

- As of now, only `USER` will use this route. So, don't worry about `CLUB` too much.

#### Exception Handling:

Raise a `HTTPException` if anything goes wrong.

#### The Response:

On completion of all the operations, return a list of all the data with a similar schema
as the following.

```json
[
  {
    "horse_selling_service_id": "horse_selling_service._id",
    "horse_id": "horses._id",
    "name": "horses.name",
    "year_of_birth": "horses.year_of_birth",
    "breed": "horses.breed",
    "size": "horses.size",
    "gender": "horses.gender",
    "description": "horses.description",
    "image_urls": [
      "horses.images[0]",
      "horses.images[1]"
    ],
    "price": "horse_selling_service.price",
    "seller_information": {
      "name": "user.name / club.name",
      "email_address": "fXXXXXXXXX@gmail.com",
      "phone_no": "+91XXXXXXXXXX",
      "location": "user.address / club.address"
    }
  }
]
```

**Notes**:

1. Use `mobodb aggregation framework` to generate the response in the `dbapis`.
2. The `email_address` of the seller will be masked in the following manner:
    1. Only first character of the `email_address` would be visible
    2. The part after the `@` would be visible.
    3. Put eight `X`s after the first character up to the `@`
    4. For example, an email address `nilanjan629@gmail.com` would be
       masked as `nXXXXXXXXXX@gmail.com`
3. The `phone_no` of the seller will be masked in the following manner:
    1. Only the first three characters would be visible
    2. Put ten `X`s after the first three character
    3. For example, a phone number `+917384927682` will be masked as
       `+91XXXXXXXXXX`
4. The `image_urls` key will contain a list of generated image urls using the
   image handling mechanism. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.

#### Pagination:

This route will need `pagination` and `filtering`. Don't worry about
it until the codebase wide `pagination-system` is implemented.


### 4. `/user/horses/update-sell-listing/{horse_selling_service_id}`

#### HTTP Method
`PUT`

#### The Process
1. `users` and `clubs` will use this route to update their sell listings.

#### Path Parameters
1. `horse_selling_service_id`: The `_id` of the `horse_selling_service` that the user wants to update.


#### Request Body
```json
{
  "name": "A name of the horse",
  "year_of_birth": "2069",
  "breed": "top class horse breed",
  "size": "size of the horse",
  "gender": "male",
  "description": "a description of the horse",
  "price": "1000 SAR"
}
```
**Notes**:
1. All the fields are optional in the request body. The provided fields will be updated. 

#### Request Validations
1. The `provider.provider_id` of the `horse_selling_service` must match
   with `user._id` or `club._id` depending on the type of the `provider`.

**Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC
1. This will be an `authenticated` route.
2. Only users with `user_role`: `USER` or `CLUB` will have the permission to acess this route.

#### The Flow:
1. Update the fields of the relevent documents of the corresponding collections
   i.e. `horse_selling_service` and `horses`. 

#### Error Handling:
Raise a `HTTPException` if anything goes wrong.

#### The Response:
On success of the prescribed operations return a generic response.

```json
  {
    "status": "OK"
  }
```

### 5. `user/horses/enquire-for-a-horse-sell`

Users will use this route to make in enquiry for a horse sell.

#### HTTP Method

`POST`

#### The Process

- User accesses the sell listing using the `/user/horses/get-horses-for-sell` route.
- User creates an enquiry for a listing. The enquiry will be visible to admins.

#### Request Body

```json
{
    "horse_selling_service_id": "the id",
    "message": "the message of the user"
}
```

#### Request Validations
1. The user must not have uploaded the `horse` which it is making an enquiry for. That is, the `provider.provider_id`
   of the `horse_selling_service` must not be the same as `user._id`.
2. The user must not have made an enquiry for the same listing already. That is, there must not be an record
   for the same `user_id` and `horse_selling_service_id` in the `horse_selling_enquiry` collection. (If the user had
   already made an enquiry he can update the existing enquiry.)

**Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC

1. This will be an `authenticated` route.
2. Only users with `user_role`: `USER` will have the permission
   to access this route.

#### The Flow

1. A new document in the `horse_selling_enquiry` collection will be created. The schema of
   the document will be similar to the following:

    ```json
    {
        "_id": ObjectId("12345"),
        "user_id": "the id of the user",
        "horse_selling_service_id": "the horse_selling_service_id",
        "message": "the message of the user"
    }
    ```

#### Exception Handling:

Raise a `HTTPException` if anything goes wrong.

#### The Response:

On completion of all the operations, return the `horse_selling_service_id`.

```json
{
  "horse_selling_enquiry_id": "the id of the newly created record"
}
```

### 6. `/user/horses/update-horse-sell-enquiry/{horse_selling_enquiry_id}`

#### HTTP Method
`PUT`

#### The Process
1. `users` will use this route to update the `sell-enquiry` it has already made using the
   `user/horses/enquire-for-a-horse-sell` route.

#### Path Parameters
1. `horse_selling_enquiry_id`: The `_id` of the `horse_selling_enquiry` that the user wants to update.


#### Request Body
```json
{
  "message": "updated message"
}
```

#### Request Validations
1. The user must be the creator of the enquiry. That is, the `horse_selling_enquiry.user_id` must
   match with the `user._id`.

**Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC
1. This will be an `authenticated` route.
2. Only users with `user_role`: `USER` will have the permission to acess this route.

#### The Flow:
1. Update the `message` of the corresponding `horse_selling_enquiry` document.

#### Error Handling:
Raise a `HTTPException` if anything goes wrong.

#### The Response:
On success of the prescribed operations return a generic response.

```json
  {
    "status": "OK"
  }
```

### 7. `/user/horses/get-horse-sell-enquiries`

- Users will use this route to get the `selling-enquiries` made by himself.
- Admins will use this route to ghet the `selling-enquiries` made by all other users.

#### HTTP Method

`GET`

#### The Process

- The `user` will use this route to get the enquiries that are made by him.
- The `admin` will use this route to ger the enquiries tha are made by all the users.


#### Authentication and RBAC

1. This will be an `authenticated` route.
2. Only users with `user_role`: `USER` and `ADMIN` will have the permission
   to access this route.

#### The Flow

1. In case it's a `USER` return all the enquiries made by the user.
2. In case it's a `ADMIN` returl all the enquiries made by all the users.

**Notes**:

- As of now, only `USER` will use this route. So, don't worry about `ADMIN` too much.

#### Exception Handling:

Raise a `HTTPException` if anything goes wrong.

#### The Response:

On completion of all the operations, return a list of all the data with a similar schema
as the following.

```json
[
    {
        "horse_selling_enquiry_id": "horse_selling_enquiry._id",
        "user_id": "horse_seling_enquiry.user_id",
        "message": "horse_selling_enquiry.message"
    }
]
```

#### Pagination:

This route will need `pagination` and `filtering`. Don't worry about
it until the codebase wide `pagination-system` is implemented.



