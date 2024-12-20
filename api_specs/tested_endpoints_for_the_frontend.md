# Tested Endpoints
The following endpoints have been put through basic automated testing. Each of the endpoints has predictable
behaviour that are well documented. This document only lists out the route names along with a brief description. 
Please visit the linked reference document for further information. 

## Onboarding 
Endpoints listed in this sub-section are primarily designed to be used in the admin app; to onboard
different types of entities such as `clubs`, `logistics-company` and so on.

### Clubs

#### 1. onboarding/create-club
One the user is created using the `auth` apis, the user will use this route to onboard
itself as a `club`. \
[Reference](onboarding_api.md#1-onboardingcreate-club)

#### 2. onboarding/club/upload-images
After onboarding as a `club` the user will use this route to upload images of the `club`. \
[Reference](onboarding_api.md#2-onboardingclubupload-images)

#### 3. onboarding/get-club
After the user onboards as a `club`, he uses this route to get details about his `club`. \
[Reference](onboarding_api.md#3-onboardingget-club)


### Logistic Company

#### 1. onboarding/create-logistic-company
Once the user is created using the `auth` apis, the user will call this api to onboard itself as a `logistic-company`. \
[Reference](onboarding_api.md#1-onboardingcreate-logistic-company)

#### 2. onboarding/logistic-company/upload-images
After onboarding as a `logistic_company`, the user will use this route to upload images of the `logistic_company`. \
[Reference](onboarding_api.md#2-onboardinglogistic-companyupload-images)

#### 3. onboarding/get-logistic-company
After the user onboards himself as a `logistic-company`, he calls this route to get details about his `logistic-company`. \
[Reference](onboarding_api.md#3-onboardingget-logistic-company)

### Trainer

#### 1. onboarding/create-trainer
Once the user is created using the `auth` apis, the user 
will call this api to onboard itself as a `trainer`. \
[Reference](onboarding_api.md#1-onboardingcreate-trainer)

#### 2. onboarding/update-trainer 
After onboarding itself as a `trainer` the user may use this route to update the details about
himself. \
[Reference](onboarding_api.md#2-onboardingupdate-trainer)

#### 3. onboarding/trainer/upload-certifications
After onboarding as a `trainer`, the user will use this route to upload certifications. \
[Reference](onboarding_api.md#3-onboardingtrainerupload-certifications)

#### 4. onboarding/trainer/upload-profile-files
After onboarding as a `trainer`, the user will use this route to upload profile files. \
[Reference](onboarding_api.md#4-onboardingtrainerupload-profile-files)

#### 5. onboarding/trainer/upload-profile-picture
After onboarding as a `trainer`, the user will use this route to upload profile picture. \
[Reference](onboarding_api.md#5-onboardingtrainerupload-profile-picture)

#### 6. onboarding/get-trainer
After the user onboards himself as a `trainer`, he calls this route to get details about the `trainer` data associated with him. \
[Reference](onboarding_api.md#6-onboardingget-trainer)

## Horse Buy Sell Rent
These routes facilitates the `horse-buy-sell-rent` functionalities. Currently, a `user` or a `club` lists a `horse`
for `sell` or `rent`. Other `users` can make an enquiry about the listing. The enquiries will be visible to the 
`khayaal-admin`.

### SELL

#### 1. user/horses/enlist-for-sell
Users will use this route to enlist new horses that is available for selling. \
[Reference](horses_buy_sell_rent_api.md#1-userhorsesenlist-for-sell)

#### 2. user/horses/{horse_selling_service_id}/upload-images
After enlisting a horse for sale using the `user/horses/enlist-horse-for-sell` route the user will use this 
route to upload images of the `horse`. \
[Reference](horses_buy_sell_rent_api.md#2-userhorseshorse_selling_service_idupload-images)

#### 3. user/horses/get-horses-for-sell
Users will use this route to get the horses:
- that are on sale and listed by others
- listed for sale by the user himself

[Reference](horses_buy_sell_rent_api.md#3-userhorsesget-horses-for-sell)

#### 4. user/horses/update-sell-listing/{horse_selling_service_id}
`Users` and `clubs` will use this route to update their sell listing. \
[Reference](horses_buy_sell_rent_api.md#4-userhorsesupdate-sell-listinghorse_selling_service_id)

#### 5. user/horses/enquire-for-a-horse-sell
Users will use this route to make in enquiry for a horse sell. \
[Reference](horses_buy_sell_rent_api.md#5-userhorsesenquire-for-a-horse-sell)

#### 6. user/horses/update-horse-sell-enquiry/{horse_selling_enquiry_id}
`Users` will use this route to update the `sell-enquiry` it has already made
using the `user/horses/enquire-for-a-horse-sell` route. \
[Reference](horses_buy_sell_rent_api.md#6-userhorsesupdate-horse-sell-enquiryhorse_selling_enquiry_id)


#### 7. user/horses/get-horse-sell-enquiries
- Users will use this route to get the `selling-enquiries` made by themselves.
- Admins will use this route to get the `selling-enquiries` made by all other users.

[Reference](horses_buy_sell_rent_api.md#7-userhorsesget-horse-sell-enquiries)

### RENT

#### 1. user/horses/enlist-for-rent
Users will use this route to enlist new horses that is available for renting. \
[Reference](horses_buy_sell_rent_api.md#1-userhorsesenlist-for-rent)

#### 2. user/horses/{horse_renting_service_id}/upload-rent-images
After enlisting a horse for rent using the `user/horses/enlist-horse-for-rent` route the user will use this 
route to upload images of the horse. \
[Reference](horses_buy_sell_rent_api.md#2-userhorseshorse_renting_service_idupload-rent-images)

#### 3. user/horses/get-horses-for-rent
Users will use this route to get horses:
- that are on `rent` and listed by others
- listed for rent by the user himself

[Reference](horses_buy_sell_rent_api.md#3-userhorsesget-horses-for-rent)

#### 4. user/horses/update-rent-listing/{horse_renting_service_id}
`users` and `clubs` will use this route to update their rent listing. \
[Reference](horses_buy_sell_rent_api.md#4-userhorsesupdate-rent-listinghorse_renting_service_id)

#### 5. user/horses/enquire-for-a-horse-rent
Users will use this route to make in enquiry for a horse rent. \
[Reference](horses_buy_sell_rent_api.md#5-userhorsesenquire-for-a-horse-rent)

#### 6. user/horses/update-horse-rent-enquiry/{horse_renting_enquiry_id}
`users` will use this route to update the `rent-enquiry` it has already made using 
the `user/horses/enquire-for-a-horse-rent` route. \
[Reference](horses_buy_sell_rent_api.md#6-userhorsesupdate-horse-rent-enquiryhorse_renting_enquiry_id)

#### 7. user/horses/get-horse-rent-enquiries
- Users will use this route to get the `renting-enquiries` made by themselves.
- Admins will use this route to get the `renting-enquirires` made by all other users.

[Reference](horses_buy_sell_rent_api.md#7-userhorsesget-horse-rent-enquiries)


## Logistics

The routes listed under this section are intended to facilitate all the `logistics` related functionalities. A few routes will be used in the admin app while others will be used in the consumer app. Please read the description and the reference to gain more insights about the intended use-cases for each of the routes.

### Logistics Trucks

Routes listed under this section are primarily intended to be used in the admin app to enable the logistic company manage trucks.

#### 1. logistic-company/trucks/add-truck
After onboarding as a logistic company the user will use this route to add trucks to offer logistic services.\
[Reference](logistics.md#1-logistic-companytrucksadd-truck)

#### 2. logistic-company/trucks/upload-truck-images/{truck_id}
After creating a new `truck` the logistic company will use this route to upload the
images associated with the `truck`.\
[Reference](logistics.md#2-logistic-companytrucksupload-truck-imagestruck_id)

#### 3. logistic-company/trucks/update-truck/{truck_id}
A logistic company uses this route to update its trucks.\
[Reference](logistics.md#3-logistic-companytrucksupdate-trucktruck_id)

#### 4. logistic-company/trucks/get-truck
A logistic company uses this route to fetch its trucks.\
[Reference](logistics.md#4-logistic-companytrucksget-truck)

#### 5. logistic-company/trucks/get-truck/{truck_id}
A logistic company uses this route to get details about a particular truck.\
[Reference](logistics.md#5-logistic-companytrucksget-trucktruck_id)


### User Logistics

This routes listed under this section are primarily intended to be used in the consumer app. These routes will enable the consumer to make bookings against logistics companies.

#### 1. user/logistics/find-nearby-trucks
The `users` of the consumer app will call this route to find nearby trucks situtated within a specified radius.\
[Reference](logistics.md#1-userlogisticsfind-nearby-trucks)

#### 2. user/logistics/create-booking
A `user` of the consumer app will user this route to create a `logistic-booking`.\
[Reference](logistics.md#2-userlogisticscreate-booking)

#### 3. user/logistics/update-booking/{logistics_service_booking_id}
A `user` of the consumer app will use tis route to update a `logistic-booking`.\
[Reference](logistics.md#3-userlogisticsupdate-bookinglogistics_service_booking_id)

#### 4. user/logistics/get-booking
This route will be used,
- by a `user` of the consumer app to get all the `logistic-bookings` made by him.
- by the `logistic_company` from the admin app to get all the `logistic-booking` that are made against that company.

[Reference](logistics.md#4-userlogisticsget-booking)







