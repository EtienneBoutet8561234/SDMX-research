from pandasdmx import Request

# Initialize a Request for the specific agency, here we use 'ESTAT'
estat = Request('ESTAT')

# Request the Data Structure Definition (DSD) for the dataflow
dsd_response = estat.datastructure('ILC_PW06')

# Get the DSD
dsd = dsd_response.structure['ILC_PW06']

# For each dimension in the DSD
for dimension in dsd.dimensions.components:
    print(f"Dimension: {dimension.id}")
    
    # Try to get the codelists for each dimension
    try:
        codelist = dimension.local_representation.enumerated
        if codelist is None:
            print(" - No valid codes")
        else:
            for code in codelist:
                print(f" - Code: {code.id}, Description: {code.name.en}")
    except AttributeError:
        print(" - Exception: dimension does not have an enumerated local representation")
