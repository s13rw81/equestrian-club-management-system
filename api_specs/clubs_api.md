# Clubs APIs
Primarily the consumer will use this set of apis. Ocassionaly, the admin app may also use the routes.

### 1. `/user/clubs/get-clubs`

The user will call this route from the consumer application to get a list of clubs with
their basic details.

#### HTTP Method
`GET`

#### The Process
- The user goes to the equestrian club section of the consumer app.
- The user calls this route to get a list of clubs with the basic details.

#### Authentication and RBAC
1. This will be an authenticated route.
2. Only users with `user_role`: `USER` will have access to this route.

#### The Flow
1. The user will call this route.
2. This route will gather data from all the relevent collections and return with the
   desired information.

#### Error Handling
Raise an `HTTPException` if anything goes wrong.

#### The Response
If everything goes well, return a response with a schema similar to the following,

```json
[
  {
    "id": "club._id",
    "name": "club.name",
    "description": "club.description",
    "average_rating": "calculate the average rating from the review collection",
    "image_urls": [
      "club.images[0]",
      "club.images[1]
    ]
  }
]
```
**Notes:**
1. To calculate the `averate_rating`, query the `review` collection. Filter all the reviews that
   matches the `reviewee.reviewee_id` with the corresponding `club._id`. Then find the average `rating`
   using the `review.rating` value. Only include the documents in the `averate_rating` calculation for which
   `approved_by_khayyal_admin` is true.
2. The `image_urls` key will contain a list of generated image urls using the
   image handling mechanism. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.

#### Pagination:

This route will need `pagination` and `filtering`. Don't worry about about it until the
codebase wide `pagination-system` is implemented.

### 2. `/user/clubs/get-club-details/{club_id}`
The user will call this route from the consumer application to get the details of a 
particular club.

#### HTTP Method
`GET`

#### Path Parameters
1. `club_id`: This will be the id of the club for which detailed information is sought.

#### The Process
- The user goes to the equestrian club section of the consumer app.
- The user calls this route to get the details of a particlar club.

#### Authentication and RBAC
1. This will be an authenticated route.
2. Only users with `user_role`: `USER` will have access to this route.

#### The Flow
1. The user will call this route.
2. This route will gather data from all the relevent collections and return with the
   desired information.

#### Error Handling
Raise an `HTTPException` if anything goes wrong.

#### The Response
If everything goes well, return a response with a schema similar to the following,

```json
{
  "id": "club._id",
  "name": "club.name",
  "description": "club.description",
  "address": "club.address",
  "location": "club.location",
  "average_rating": "calculate the average rating from the review collection",
  "is_khayyal_verified": "club.is_khayyal_verified",
  "trainers": [
    {
      "id": "trainer.id",
      "full_name": "trainer.full_name"
    }
  ]
  "image_urls": [
    "club.images[0]",
    "club.images[1]"
  ],
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
**Notes:**
1. To calculate the `average_rating`, query the `review` collection. Filter all the reviews that
   matches the `reviewee.reviewee_id` with the corresponding `club._id`. Then find the average `rating`
   using the `review.rating` value. Only include the documents in the `averate_rating` calculation for which
   `approved_by_khayyal_admin` is true.
2. For `trainers` query the `trainer` collection and return all the `trainers` in the
   prescribed format associated with the club. The `foreign_key` in the `trainer`
   collection is `club_id`, it matches with the `club._id`.  
4. The `image_urls` key will contain a list of generated image urls using the
   image handling mechanism. To learn how to use the image handling mechanism refer
   to the [Notes on handling images](../README.md#notes-on-handling-images) section
   of the `README.md` file.
5. Fetch `riding_lesson_service` from the `riding_lesson_service` collection.
6. Fetch `horse_shoeing_service` from the `horse_shoeing_service` collection.
7. Fetch `genetic_activity_service` from the `generic_activity_service` collection.
8. Use `monbodb aggregation framework` to generate the response in the `dbapis`.


### 3. `/users/club/book-riding-lesson-service/{club_id}`
The consumer will use this route to book `riding_lesson_service` of a club.

#### HTTP Method
`POST`

#### Path Parameters
1. `club_id`: The `id` of the `club` against which booking is being made.

#### The Process
- The `user` uses the `/user/clubs/get-club-details/{club_id}` route to fetch the details
  of a club. The response includes the data about the `riding_lesson_service` the `club`
  offers.
- The `user`, in turn, uses this route to make a booking against the `riding_lesson_service`
  the `club` is offering.

#### Request Body

```json
{
  "trainer_id": "the chosen id of the trainer",
  "date": "the chosen date",
  "pricing_option": "the chosen pricing option",
  "number_of_visitrs": "number of visitors that are coming"
}
```

#### Request Validations
1. The `trainer_id` must be associated with the coresponding `club`.
2. The `date` must not be from the past.
3. The `pricing_option` must be one of the `pricing_option`s offered by the club. To
   validate this, query the `riding_lesson_service` collection to find out whether the
   `club` offers the provided `pricing_option`.
4. All the fields are mandatory.
5. A field of type `string` is not allowed to have an empty string. 

  **Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC
1. This would be an authenticated route.
2. The user must have the role `UserRoles.USER`

#### The Flow
1. Create a new document in the `riding_lesson_service_booking` collection.
   The schema of the document will be similar to the following:
    ```json
      {
        "_id": ObjectId("12345"),
        "user_id": "the id of the user who's making the bookinng",
        "riding_lesson_service_id": "the id of the riding_lesson_service, figure this out based on the club_id",
        "trainer_id": "the chosen id of the trainer",
        "selected_date": "the chosen date",
        "pricing_option": "the chosen pricing_option",
        "number_of_visitors": "the number fo visitors"
      }
    ```
**Note**: Use transactions for the database operations. **(Ignore this requirement until transaction management system is implemented.)**

#### Error Hadling

Raise a `HTTPException` if anything goes wrong.

#### The Response

If all the prescribed operations succeed return the newly created `id` of the `riding_lesson_service_booking`
document.

```json
{"riding_lesson_service_booking_id": "the id of the newly created service booking"}
```

### 4. `/users/club/book-horse-shoeing-service/{club_id}`
The consumer will use this route to book `horse_shoeing_service` of a club.

#### HTTP Method
`POST`

#### Path Parameters
1. `club_id`: The `id` of the `club` against which booking is being made.

#### The Process
- The `user` uses the `/user/clubs/get-club-details/{club_id}` route to fetch the details
  of a club. The response includes the data about the `horse_shoeing_service` the `club`
  offers.
- The `user`, in turn, uses this route to make a booking against the `horse_shoeing_service`
  the `club` is offering.

#### Request Body

```json
{
  "farrier_id": "this will be a trainer_id",
  "date": "the chosen date",
  "pricing_option": "the chosen pricing option",
  "horse_name": "the name of the horse"
}
```

#### Request Validations
1. The `trainer_id` must be associated with the coresponding `club`.
2. The `date` must not be from the past.
3. The `pricing_option` must be one of the `pricing_option`s offered by the club. To
   validate this, query the `horse_shoeing_service` collection to find out whether the
   `club` offers the provided `pricing_option`.
4. All fields are mandatory.
5. A field of type `string` is not allowed to be an empty string.

  **Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC
1. This would be an authenticated route.
2. The user must have the role `UserRoles.USER`

#### The Flow
1. Create a new document in the `horse_shoeing_service_booking` collection.
   The schema of the document will be similar to the following:
    ```json
      {
        "_id": ObjectId("12345"),
        "user_id": "the id of the user who's making the bookinng",
        "horse_shoeing_service_id": "the id of the horse_shoeing_service, figure this out based on the club_id",
        "farrier_id": "the chosen id, this will be a trainer._id",
        "selected_date": "the chosen date",
        "pricing_option": "the chosen pricing_option",
        "horse_name": "the horse_name provided by the user"
      }
    ```
**Note**: Use transactions for the database operations. **(Ignore this requirement until transaction management system is implemented.)**

#### Error Hadling

Raise a `HTTPException` if anything goes wrong.

#### The Response

If all the prescribed operations succeed return the newly created `id` of the `horse_shoeing_service_booking`
document.

```json
{"horse_shoeing_service_booking_id": "the id of the newly created service booking"}
```

### 5. `/users/club/book-generic-activity-service/{club_id}`
The consumer will use this route to book `generic_activity_service` of a club.

#### HTTP Method
`POST`

#### Path Parameters
1. `club_id`: The `id` of the `club` against which booking is being made.

#### The Process
- The `user` uses the `/user/clubs/get-club-details/{club_id}` route to fetch the details
  of a club. The response includes the data about the `generic_activity_service` the `club`
  offers.
- The `user`, in turn, uses this route to make a booking against the `generic_activity_service`
  the `club` is offering.

#### Request Body

```json
{
  "trainer_id": "this will be a trainer_id",
  "date": "the chosen date",
  "number_of_people": "number of people"
}
```

#### Request Validations
1. The `trainer_id` must be associated with the coresponding `club`.
2. The `date` must not be from the past.
3. All fields are mandatory.
4. A field of type `string` is not allowed to be an empty string.

  **Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC
1. This would be an authenticated route.
2. The user must have the role `UserRoles.USER`

#### The Flow
1. Create a new document in the `generic_activity_service_booking` collection.
   The schema of the document will be similar to the following:
    ```json
      {
        "_id": ObjectId("12345"),
        "user_id": "the id of the user who's making the bookinng",
        "generic_activity_service_id": "the id of the generic_activity_service, figure this out based on the club_id",
        "trainer_id": "the chosen id of the trainer",
        "selected_date": "the chosen date",
        "price": "figure out the price based on the generic_activity_service of the club",
        "number_of_people": "the number of people provided by the user"
      }
    ```
**Note**: Use transactions for the database operations. **(Ignore this requirement until transaction management system is implemented.)**

#### Error Hadling

Raise a `HTTPException` if anything goes wrong.

#### The Response

If all the prescribed operations succeed return the newly created `id` of the `generic_activity_service_booking`
document.

```json
{"generic_activity_service_booking_id": "the id of the newly created service booking"}
```

### 6. `/user/club/get-riding-lesson-service-booking`
This route will be used by multiple types of users. Depending on the type of the user
the response may vary. In general, it would return a list of `riding_lesson_service_booking`. 

#### HTTP Method
`GET`

#### The Process
- A normal `user` will call this route from the consumer app to get the `riding_lesson_service_booking` made by him.
- A `club` will call this route from the admin app to get the `riding_lesson_service_booking` made by all the users with the specific club.
- A `khayyal-admin` will call this route to get all the `riding_lesson_service_booking` available in the database.


#### Authentication and RBAC
1. This will be an authenticated route.
2. Only users with `user_role`: `USER` or `user_role`: `CLUB` or `user_role`: `ADMIN` will have access to this route.

#### The Flow
1. If a `user` with `user_role`: `USER` calls this route, return the `riding_lesson_service_booking` made by that `user` only.
2. If a user with `user_role`: `CLUB` calls this route, return the `riding_lesson_service_booking` made with the `club` only.
3. If a user with `user_role`: `ADMIN` calls this route, return all the `riding_lesson_service_booking` available in the database.
4. The collection name in the database is the same as well: `riding_lesson_service_booking`.

#### Error Handling
Raise an `HTTPException` if anything goes wrong.

#### The Response
If everything goes well return a response with a schema similar to the following:

```json
[
   {
      "user_id": "riding_lesson_service_booking.user_id",
      "riding_lesson_service_id": "riding_lesson_service_booking.riding_lesson_service_id",
      "club_id": "the club_id associated with the riding_lesson_service",
      "trainer_id": "riding_lesson_service_booking.trainer_id",
      "selected_date": "riding_lesson_service_booking.selected_date",
      "pricing_option": "riding_lesson_service_booking.pricing_option",
      "number_of_visitors": "riding_lesson_service_booking.number_of_visitors"
   }
]
```

#### Pagination

This route will need `pagination` and `filtering`. Don't worry about it until codebase wide `pagination-system` is implemented.


### 7. `/user/club/get-horse-shoeing-service-booking`
This route will be used by multiple types of users. Depending on the type of the user
the response may vary. In general, it would return a list of `horse_shoeing_service_booking`. 

#### HTTP Method
`GET`

#### The Process
- A normal `user` will call this route from the consumer app to get the `horse_shoeing_service_booking` made by him.
- A `club` will call this route from the admin app to get the `horse_shoeing_service_booking` made by all the users with the specific club.
- A `khayyal-admin` will call this route to get all the `horse_shoeing_service_booking` available in the database.


#### Authentication and RBAC
1. This will be an authenticated route.
2. Only users with `user_role`: `USER` or `user_role`: `CLUB` or `user_role`: `ADMIN` will have access to this route.

#### The Flow
1. If a `user` with `user_role`: `USER` calls this route, return the `horse_shoeing_service_booking` made by that `user` only.
2. If a user with `user_role`: `CLUB` calls this route, return the `horse_shoeing_service_booking` made with the `club` only.
3. If a user with `user_role`: `ADMIN` calls this route, return all the `horse_shoeing_service_booking` available in the database.
4. The collection name in the database is the same as well: `horse_shoeing_service_booking`.

#### Error Handling
Raise an `HTTPException` if anything goes wrong.

#### The Response
If everything goes well return a response with a schema similar to the following:

```json
[
   {
      "user_id": "horse_shoeing_service_booking.user_id",
      "horse_shoeing_service_id": "horse_shoeing_service_booking.horse_shoeing_service_id",
      "club_id": "the club_id associated with the horse_shoeing_service",
      "farrier_id": "horse_shoeing_service_booking.farrier_id",
      "selected_date": "horse_shoeing_service_booking.selected_date",
      "pricing_option": "horse_shoeing_service_booking.pricing_option",
      "horse_name": "horse_shoeing_service_booking.horse_name"
   }
]
```

#### Pagination

This route will need `pagination` and `filtering`. Don't worry about it until codebase wide `pagination-system` is implemented.

### 8. `/user/club/get-generic-activity-service-booking`
This route will be used by multiple types of users. Depending on the type of the user
the response may vary. In general, it would return a list of `generic_activity_service_booking`. 

#### HTTP Method
`GET`

#### The Process
- A normal `user` will call this route from the consumer app to get the `generic_activity_service_booking` made by him.
- A `club` will call this route from the admin app to get the `generic_activity_service_booking` made by all the users with the specific club.
- A `khayyal-admin` will call this route to get all the `generic_activity_service_booking` available in the database.


#### Authentication and RBAC
1. This will be an authenticated route.
2. Only users with `user_role`: `USER` or `user_role`: `CLUB` or `user_role`: `ADMIN` will have access to this route.

#### The Flow
1. If a `user` with `user_role`: `USER` calls this route, return the `generic_activity_service_booking` made by that `user` only.
2. If a user with `user_role`: `CLUB` calls this route, return the `generic_activity_service_booking` made with the `club` only.
3. If a user with `user_role`: `ADMIN` calls this route, return all the `generic_activity_service_booking` available in the database.
4. The collection name in the database is the same as well: `generic_activity_service_booking`.

#### Error Handling
Raise an `HTTPException` if anything goes wrong.

#### The Response
If everything goes well return a response with a schema similar to the following:

```json
[
   {
      "user_id": "generic_activity_service_booking.user_id",
      "generic_activity_service_id": "generic_activity_service_booking.generic_activity_service_id",
      "club_id": "the club_id associated with the generic_activity_service",
      "tariner_id": "generic_activity_service_booking.trainer_id",
      "selected_date": "generic_activity_service_booking.selected_date",
      "price": "generic_activity_service_booking.pricing_option",
      "number_of_people": "generic_activity_service_booking.number_of_people"
   }
]
```

#### Pagination

This route will need `pagination` and `filtering`. Don't worry about it until codebase wide `pagination-system` is implemented.


### 9. `/users/club/rate-a-club`
The consumer will use this route provide `rating` and `review` to a club.

#### HTTP Method
`POST`


#### The Process
- The user will navigate to the `reviews` page of the `club`. In this page, the user will be shown the average rating and the list of reviews.
- In case the user choses to leave a `rating` with or without a review, the user will call this route.

#### Request Body

```json
{
   "club_id": "the id of the club",
   "rating": 4,
   "review": "this club provides good services"
}
```

#### Request Validations
1. The `club_id` must be a valid `club_id`.
2. The user must not have reviewed the club previously. That means in the `review` collection there must not exist an entry where the `reviewer.reviewer_id` matches the `user._id` and the `reviewee.reviewee_id` matches the provided `club_id`. In this case the user must use the update route to update the existing review.
3. The `rating` will be an int ranging from 1-5.
4. All the fields are mandatory unless otherwise explicitly mentioned.
5. The `review` is optional.


   **Note**: Use `pydantic` validators for the validations.

#### Authentication and RBAC
1. This would be an authenticated route.
2. The user must have the role `UserRoles.USER`

#### The Flow
1. Create a new document in the `review` collection.
   The schema of the document will be similar to the following:
```json
   {
      "_id": ObjectId("12345"),
      "reviewee": {
         "reviewee_id": "club_id",
         "reviewee_type": "CLUB"
      },
      "reviewer": {
         "reviewer_id": "user._id",
         "reviewer_type": "USER"
      },
      "rating": "provided rating",
      "review": "provided review",
      "approved_by_khayyal_admin": false
   }
```
   **Note**: Use transactions for the database operations. **(Ignore this requirement until transaction management system is implemented.)**

#### Error Hadling

Raise a `HTTPException` if anything goes wrong.

#### The Response

If all the prescribed operations succeed return the newly created `id` of the `review`
document.

```json
{"review_id": "review._id"}
```


