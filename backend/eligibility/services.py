from datetime import date

VALUE_EQUIVALENCE_GROUPS = {
    "course": (("BE_BTECH", "ENGG", "ENGINEERING"),),
}


def _normalize_eligibility_value(value):
    return "".join(character for character in value.casefold() if character.isalnum())


def _eligibility_value_keys(field_name, values):
    keys = {
        _normalize_eligibility_value(value.strip())
        for value in values
        if value and value.strip()
    }

    for group in VALUE_EQUIVALENCE_GROUPS.get(field_name, ()):
        normalized_group = {
            _normalize_eligibility_value(value) for value in group
        }
        if keys.intersection(normalized_group):
            keys.update(normalized_group)

    return keys


def _matches_profile_value(student, field_name, option):
    student_value = getattr(student, field_name)
    if not student_value or not student_value.strip():
        return False

    profile_values = [student_value]
    normalized_student_value = _normalize_eligibility_value(
        student_value.strip()
    )
    for code, label in student._meta.get_field(field_name).choices:
        if _normalize_eligibility_value(code) == normalized_student_value:
            profile_values.append(label)
            break

    scholarship_values = [option.code or "", option.name]
    return bool(
        _eligibility_value_keys(field_name, profile_values)
        & _eligibility_value_keys(field_name, scholarship_values)
    )


def check_percentage(scholarship, student):
    minimum = scholarship.minimum_percentage
    percentage = student.percentage

    if minimum is None:
        return {
            "status": "not_applicable",
            "reason": "No minimum percentage required.",
        }

    if percentage is None:
        return {
            "status": "unknown",
            "reason": "Student percentage has not been provided.",
        }

    if percentage >= minimum:
        return {
            "status": "passed",
            "reason": f"Required: {minimum}%, student has: {percentage}%.",
        }

    return {
        "status": "failed",
        "reason": f"Required: {minimum}%, student has: {percentage}%.",
    }


def check_cgpa(scholarship, student):
    minimum = scholarship.minimum_cgpa
    cgpa = student.cgpa

    if minimum is None:
        return {
            "status": "not_applicable",
            "reason": "No minimum CGPA required.",
        }

    if cgpa is None:
        return {
            "status": "unknown",
            "reason": "Student CGPA has not been provided.",
        }

    if cgpa >= minimum:
        return {
            "status": "passed",
            "reason": f"Required: {minimum}, student has: {cgpa}.",
        }

    return {
        "status": "failed",
        "reason": f"Required: {minimum}, student has: {cgpa}.",
    }


def check_family_income(scholarship, student):
    maximum = scholarship.maximum_family_income
    income = student.family_income

    if maximum is None:
        return {
            "status": "not_applicable",
            "reason": "No maximum family income requirement.",
        }

    if income is None:
        return {
            "status": "unknown",
            "reason": "Student family income has not been provided.",
        }

    if income <= maximum:
        return {
            "status": "passed",
            "reason": f"Maximum allowed: ₹{maximum}, student income: ₹{income}.",
        }

    return {
        "status": "failed",
        "reason": f"Maximum allowed: ₹{maximum}, student income: ₹{income}.",
    }


def check_age(scholarship, student):
    minimum = scholarship.minimum_age
    maximum = scholarship.maximum_age
    dob = student.date_of_birth

    if minimum is None and maximum is None:
        return {
            "status": "not_applicable",
            "reason": "No age requirement.",
        }

    if dob is None:
        return {
            "status": "unknown",
            "reason": "Student date of birth has not been provided.",
        }

    today = date.today()
    age = today.year - dob.year

    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1

    if minimum is not None and age < minimum:
        return {
            "status": "failed",
            "reason": f"Minimum age: {minimum}, student age: {age}.",
        }

    if maximum is not None and age > maximum:
        return {
            "status": "failed",
            "reason": f"Maximum age: {maximum}, student age: {age}.",
        }

    return {
        "status": "passed",
        "reason": f"Student age: {age}; age requirements satisfied.",
    }


def check_gender(scholarship, student):
    required = scholarship.gender
    gender = student.gender

    if required is None or required == "any":
        return {
            "status": "not_applicable",
            "reason": "No specific gender requirement.",
        }

    if not gender or gender == "PREFER_NOT_TO_SAY":
        return {
            "status": "unknown",
            "reason": "Student gender is unavailable for this check.",
        }

    # Scholarship values are lowercase; student values are uppercase.
    if gender.lower() == required.lower():
        return {
            "status": "passed",
            "reason": f"Required gender: {required}.",
        }

    return {
        "status": "failed",
        "reason": f"Required gender: {required}; student gender: {gender}.",
    }


def check_category(scholarship, student):
    allowed_categories = scholarship.category.all()
    student_category = student.category

    if not allowed_categories.exists():
        return {
            "status": "not_applicable",
            "reason": "No category restriction.",
        }

    if not student_category or not student_category.strip():
        return {
            "status": "unknown",
            "reason": "Student category has not been provided.",
        }

    for category in allowed_categories:
        if _matches_profile_value(student, "category", category):
            return {
                "status": "passed",
                "reason": f"Student category {student_category} is accepted.",
            }

    return {
        "status": "failed",
        "reason": f"Student category {student_category} is not accepted.",
    }


def check_state(scholarship, student):
    allowed_states = scholarship.state.all()
    student_state = student.state

    if not allowed_states.exists():
        return {
            "status": "not_applicable",
            "reason": "No state restriction.",
        }

    if not student_state:
        return {
            "status": "unknown",
            "reason": "Student state has not been provided.",
        }

    for state in allowed_states:
        if state.code and state.code.upper() == student_state.upper():
            return {
                "status": "passed",
                "reason": f"Student state {student_state} is accepted.",
            }

    return {
        "status": "failed",
        "reason": f"Student state {student_state} is not accepted.",
    }


def check_district(scholarship, student):
    allowed_districts = scholarship.district.all()
    student_district = student.district

    if not allowed_districts.exists():
        return {
            "status": "not_applicable",
            "reason": "No district restriction.",
        }

    if not student_district or not student_district.strip():
        return {
            "status": "unknown",
            "reason": "Student district has not been provided.",
        }

    student_value = student_district.strip().casefold()

    for district in allowed_districts:
        if (
            (district.code and district.code.strip().casefold() == student_value)
            or district.name.strip().casefold() == student_value
        ):
            return {
                "status": "passed",
                "reason": f"Student district {student_district} is accepted.",
            }

    return {
        "status": "failed",
        "reason": f"Student district {student_district} is not accepted.",
    }


def check_course(scholarship, student):
    allowed_courses = scholarship.course.all()
    student_course = student.course

    if not allowed_courses.exists():
        return {
            "status": "not_applicable",
            "reason": "No course restriction.",
        }

    if not student_course or not student_course.strip():
        return {
            "status": "unknown",
            "reason": "Student course has not been provided.",
        }

    for course in allowed_courses:
        if _matches_profile_value(student, "course", course):
            return {
                "status": "passed",
                "reason": f"Student course {student_course} is accepted.",
            }

    return {
        "status": "failed",
        "reason": f"Student course {student_course} is not accepted.",
    }


def check_branch(scholarship, student):
    allowed_branches = scholarship.branch.all()
    student_branch = student.branch

    if not allowed_branches.exists():
        return {
            "status": "not_applicable",
            "reason": "No branch restriction.",
        }

    if not student_branch or not student_branch.strip():
        return {
            "status": "unknown",
            "reason": "Student branch has not been provided.",
        }

    for branch in allowed_branches:
        if _matches_profile_value(student, "branch", branch):
            return {
                "status": "passed",
                "reason": f"Student branch {student_branch} is accepted.",
            }

    return {
        "status": "failed",
        "reason": f"Student branch {student_branch} is not accepted.",
    }


def check_year_of_study(scholarship, student):
    required_year = scholarship.year_of_study
    student_year = student.year_of_study

    if required_year is None or required_year == "any":
        return {
            "status": "not_applicable",
            "reason": "No specific year-of-study restriction.",
        }

    if required_year == "postgraduate":
        postgraduate_courses = {"ME_MTECH", "MSC", "MCA", "MBA"}

        if not student.course:
            return {
                "status": "unknown",
                "reason": "Student course has not been provided.",
            }

        if student.course in postgraduate_courses:
            return {
                "status": "passed",
                "reason": "Student is enrolled in a postgraduate course.",
            }

        return {
            "status": "failed",
            "reason": "Scholarship is restricted to postgraduate students.",
        }

    if student_year is None:
        return {
            "status": "unknown",
            "reason": "Student year of study has not been provided.",
        }

    if student_year == int(required_year):
        return {
            "status": "passed",
            "reason": f"Student is in year {student_year}, as required.",
        }

    return {
        "status": "failed",
        "reason": f"Required year: {required_year}; student year: {student_year}.",
    }


def check_pwd(scholarship, student):
    required = scholarship.pwd
    student_pwd = student.pwd

    if required is None:
        return {
            "status": "not_applicable",
            "reason": "No PwD-specific requirement.",
        }

    if student_pwd is None:
        return {
            "status": "unknown",
            "reason": "Student PwD status has not been provided.",
        }

    if student_pwd == required:
        return {
            "status": "passed",
            "reason": "Student PwD status matches the scholarship requirement.",
        }

    return {
        "status": "failed",
        "reason": "Student PwD status does not match the scholarship requirement.",
    }


def check_minority(scholarship, student):
    required = scholarship.minority
    student_minority = student.minority

    if required is None:
        return {
            "status": "not_applicable",
            "reason": "No minority-status requirement.",
        }

    if student_minority is None:
        return {
            "status": "unknown",
            "reason": "Student minority status has not been provided.",
        }

    if student_minority == required:
        return {
            "status": "passed",
            "reason": "Student minority status matches the scholarship requirement.",
        }

    return {
        "status": "failed",
        "reason": "Student minority status does not match the scholarship requirement.",
    }


def evaluate_eligibility(scholarship, student):
    criteria = {
        "percentage": check_percentage(scholarship, student),
        "cgpa": check_cgpa(scholarship, student),
        "family_income": check_family_income(scholarship, student),
        "age": check_age(scholarship, student),
        "gender": check_gender(scholarship, student),
        "category": check_category(scholarship, student),
        "state": check_state(scholarship, student),
        "district": check_district(scholarship, student),
        "course": check_course(scholarship, student),
        "branch": check_branch(scholarship, student),
        "year_of_study": check_year_of_study(scholarship, student),
        "pwd": check_pwd(scholarship, student),
        "minority": check_minority(scholarship, student),
    }

    statuses = [result["status"] for result in criteria.values()]

    if "failed" in statuses:
        overall_status = "ineligible"
    elif "unknown" in statuses:
        overall_status = "incomplete"
    else:
        overall_status = "eligible"

    return {
        "scholarship_id": scholarship.id,
        "scholarship_name": scholarship.name,
        "overall_status": overall_status,
        "criteria": criteria,
    }
