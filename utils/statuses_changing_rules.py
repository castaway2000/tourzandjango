
def checking_statuses(current_status_id, new_status_id):
    current_status_id = int(current_status_id)
    new_status_id = int(new_status_id)

    print (new_status_id)
    print (new_status_id==2)
    if new_status_id == 1:
        return False

    #for testing purposes of payments !!! Delete this for production
    elif new_status_id == 4:
        return True


    elif new_status_id == 2 and current_status_id != 5:
        return False

    elif new_status_id in [3, 6] and not current_status_id in [1, 2, 5]:
        return False
    elif new_status_id == 4 and current_status_id != 2:
        return False
    elif new_status_id == 5 and current_status_id != 4:
        return False
    else:
        return True