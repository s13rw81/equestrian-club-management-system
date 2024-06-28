# Onboarding API

This set of apis will be used to onboard different types of entities
primarily from the admin app after creation of the user. This includes,
- logistic-company
- club
- trainer

### 1. `onboarding/create-logistic-company`
Once the user is created using the `auth` apis the user 
will call this api to onboard itself as a `logistic-company`.

### HTTP Method
`POST`

### The Process
- the user signs up using the `users/signup` route
- the newly onboarded user, in turn, calls the `auth/generate-signup-otp` route
- the user verifies the otp using the `auth/verify-signup-otp` route
- the user calls the `onboarding/create-logistic-company` route to onboard itself as a `logistic-company`

### Request Body

```json
{
  "email_address": "someemail@domain.com",
  "phone_no": "+911111111111",
  "name": "name of the logistic-company",
  "description": "a description of the company"
}
```

### Request Validations
1. A `logistic-company` with the same `email_address` must not exist
2. The user's `otp_verified` must be `true`

**Note**: Use `pydantic` validators for the validations

### Authentication and RBAC
1. This would be an authenticated route
2. The user must have the role `UserRoles.USER`

### The Flow
1. A new document would be created in the `logistic_companies` collection.
The document in the collection will be similar to the following:
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

### The Response

If all the validations pass the request would also succeed. If anything
else goes wrong the pipeline exception handler to catch the error.

Typically, the request would succeed and return,

```json
{"logistic_company_id":  "the id of the newly created company"}
```

