# Name of the Group that indicates a User is a trainer.
TRAINERS_GROUP = 'Trainers'

# Group names with this prefix indicate a location.
LOCATION_GROUP_PREFIX = 'location:'


# Is a Group name a location?
def is_loc(group_name):
	return group_name.lower().startswith(LOCATION_GROUP_PREFIX)

# Extract the location-name from a Group name.
def loc_name(group_name):
	return group_name[len(LOCATION_GROUP_PREFIX):].strip()

# Get the location Groups for a given User.
def loc_groups(user):
	return user.groups.filter(name__istartswith=LOCATION_GROUP_PREFIX)
