from fastapi import Query


def parse_query_parameters_as_list_int(favorite_list: str = Query(example='1,2,3')):
    return [int(pair_id) for pair_id in favorite_list.split(',')]
