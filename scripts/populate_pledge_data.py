

from apps.volunteers.models import Ward, Area, Organization, OrganizationType

def run():
    w1, _ = Ward.objects.get_or_create(name="Naroda East")
    w2, _ = Ward.objects.get_or_create(name="Naroda West")

    Area.objects.get_or_create(ward=w1, name="Krishnanagar")
    Area.objects.get_or_create(ward=w1, name="Nikol Road")
    Area.objects.get_or_create(ward=w2, name="GIDC")
    Area.objects.get_or_create(ward=w2, name="Sardar Patel Ring Road")

    Organization.objects.get_or_create(name="Rotary Club", org_type=OrganizationType.NGO)
    Organization.objects.get_or_create(name="Lions Club", org_type=OrganizationType.NGO)
    Organization.objects.get_or_create(name="Green Volunteers", org_type=OrganizationType.VOLUNTEER_GROUP)

    print("Data populated!")

if __name__ == "__main__":
    run()
