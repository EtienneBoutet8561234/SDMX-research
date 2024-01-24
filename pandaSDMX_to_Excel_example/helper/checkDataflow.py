from pandasdmx import Request

estat = Request('ESTAT')

dataflows_response = estat.dataflow()

# Print the IDs of all dataflows
for df in dataflows_response.dataflow.values():
    print(df.id)
