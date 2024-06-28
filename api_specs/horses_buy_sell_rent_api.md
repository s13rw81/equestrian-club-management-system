# Horses buy-sell-rent API

This set of apis will be utilized to manage the buy, sell and rent of
the horses. The `users` and `clubs` will enlist horses for others
to buy or rent. As of now, `users` will be able to see the listing and make
enquiry for the listing. The `enquiries` will be accessible by `khayyal-admin`.

### 1. `user/horses/enlist-for-sell` 

Users will use this route to enlist new horses that is available for selling. 

####

#### The Process
- The user signs up using the `users/signup` route
- The user use this route to enlist a horse for selling
- This route may also be used by a `club`
- The differences between a `user` and a `club` are the following: 
  1. firstly, the`user_role` of an `user` is set to `USER`, for a club it's `CLUB`. 
  2. Secondly, a `club` has a `club` entity associated with it. The 
  corresponding `club` entity can be found from the `clubs` collection.



