Search by Radius Service - Last Sale


GET
/search/au/property/geo/radius/lastSale
Search by Radius - Last Sale


Use the Search by Radius - Last Sale service to get a list of properties based on their last sale date, surrounding a geographical point. You can filter and sort the results based on multiple parameters. The response includes a list of properties with property summary and the last sale data. The results in the response are sorted in ascending order based on the distance of the property from the specified geographical point.

Parameters
Try it out
Name	Description
lat
(query)
The latitude coordinate of the central point to conduct the radius search. This is mandatory, if propertyId is not passed.

lat
lon
(query)
The longitude coordinate of the central point to conduct the radius search. This is mandatory, if propertyId is not passed.

lon
propertyId
(query)
The unique ID of the property. This is mandatory, if lat&lon are not passed.

propertyId
radius *
(query)
The radius, in kilometres, used to perform the search around the latitude and longitude provided. This is mandatory and accepts values up to a maximum of 100.

radius
localityId
(query)
Locality search filter. The filter allows the users to retrieve a list of properties for a specific locality. Can include the filter as a single value or multiple values separated by comma. For example, following the syntax &localityId={localityId},{localityId}...

localityId
postCodeId
(query)
Postcode search filter. The filter allows the users to retrieve a list of properties for a specific postcode. Can include the filter as a single value or multiple values separated by comma. For example, following the syntax &postCodeId={postCodeId},{postCodeId}...

postCodeId
streetId
(query)
Street search filter. The filter allows the users to retrieve a list of properties for a specific street. Can include the filter as a single value or multiple values separated by comma.For example, following the syntax &streetId={streetId},{streetId}...

streetId
price
(query)
The sale price of the property. Use this to filter the results based on the price of the last sale. You can either pass the exact amount or a range of amounts. If you specify:

price=500000, the response includes all the properties that have their last sale price as $500,000.
price=515000-550000, the response includes all the properties that have the last sale price between $515,000 and $550,000.
price=550000-, the response includes all the properties that have the last sale price as $550,000 or above.
price=-550000, the response includes all the properties that have the last sale price as $550,000 and below.
price
date
(query)
The date of the property's last sale, as recorded by CoreLogic. Use this to filter the results based on the date associated with the last sale.

The date value must be in the format YYYYMMDD (ISO 8601 format without the hyphens)

You can either pass the exact date or a range of dates. If you specify:

date=20160101, the response includes all the properties that have their sale date as January 1, 2016.
date=20151201-20151231, the response includes all the properties that have the last sale date between December 1, 2015, to December 31, 2015.
date=20160101-, the response includes all the properties that have the last sale date from January 1, 2016, to today.
date=-20160101, the response includes all the properties that have the last sale date before January 1, 2016.
date
source
(query)
Use this parameter to filter the results based on the source type associated with the sale. Available values for this parameter are:

AA to only return properties with sales advised by Agents.
ALL to return properties with sales advised by either Agent or the Valuer-General.
VG to only return properties with sales advised by the Valuer-General.
source
baths
(query)
The number of bathrooms. Use this to filter the matched properties. You can either pass the exact value or a range of values.

Exact value
If you specify baths=4, the response includes all the properties with exactly 4 bathrooms.
Range of values
If you specify baths=2-5, the response includes all the properties where the number of bathrooms is between 2 and 5.
If you specify baths=3-, the response includes all the properties with 3 or more bathrooms.
If you specify baths=-4, the response includes all the properties with 4 or fewer bathrooms.
baths
beds
(query)
The number of bedrooms. Use this to filter the matched properties. You can either pass the exact value or a range of values.

Exact value
If you specify beds=4, the response includes all the properties with exactly 4 bedrooms.
Range of values
If you specify beds=2-5, the response includes all the properties where the number of bedrooms is between 2 and 5.
If you specify beds=3-, the response includes all the properties with 3 or more bedrooms.
If you specify beds=-4, the response includes all the properties with 4 or fewer bedrooms.
beds
carSpaces
(query)
The number of car spaces. Use this to filter the matched properties. You can either pass the exact value or a range of values.

Exact value
If you specify carSpaces=2, the response includes all the properties with exactly 2 car spaces.
Range of values
If you specify carSpaces=1-3, the response includes all the properties where the number of car spaces is between 1 and 3.
If you specify carSpaces=1-, the response includes all the properties with 1 or more car spaces.
If you specify carSpaces=-3, the response includes all the properties with 3 or fewer car spaces.
carSpaces
landArea
(query)
The property's land area in meters squared (m²). Use this to filter the matched properties.
You can either pass the exact value or a range of values.

Exact value
If you specify landArea=300, the response includes all the properties with exactly 300 m² land area.
Range of values
If you specify landArea=300-600, the response includes all the properties where the land area is between 300 m² and 600 m².
If you specify landArea=300-, the response includes all the properties with land area 300 m² or above.
If you specify landArea=-600, the response includes all the properties with land area 600 m² or less.
landArea
includeHistoric
(query)
includeHistoric
pTypes
(query)
The type of the property. Use this to filter the matched properties. You can either pass a single value or a comma-separated list of allowed values.

Single value
If you specify pType=UNIT, the response includes all the properties which are of type UNIT.
Multiple values
If you specify pType=LAND, COMMERCIAL, OTHER, the response includes all the properties which are of type LAND, or COMMERCIAL, or OTHER.
The available types are:

BUSINESS
COMMERCIAL
COMMUNITY
FARM
FLATS
HOUSE
LAND
OTHER
STORAGE_UNIT
UNIT
pTypes
sort
(query)
The sorting criteria. Use this to sort the matched results based on a specific parameter in a particular order. To sort using more than one parameters, specify multiple sort values in your query in the following format:
sort={attribute_1},{sort_order}&sort={attribute_2},{sort_order}...&{attribute_n},{sort_order}

Available attributes are:

bath
beds
carSpaces
landArea
pType
Sort order can be either asc for ascending or desc for descending order.

If you do not specify a sort order, the results are sorted in ascending order by default.

Example:

Specify sort=beds,desc to sort the results based on the number of beds and arranged in descending order.
sort
size
(query)
Use this parameter to specify the number of records per page. By default, the response contains 20 records per page.

Any higher value than 20 results in an invalid request.

size
page
(query)
Use this parameter to specify the page number of the results to return. By default, this always returns the first page (that is page=0).

page
Responses
Response content type

application/json
Code	Description
200	
OK

400	
Page size cannot exceed 20.
Invalid request parameter value for <parameterName> provided.
Either lat&lon or propertyId is mandatory.
radius: Missing mandatory parameter, radius.
radius: Exceeds the limit of 100

401	
Unauthorized

403	
Forbidden

404	
Property id does not exist.
Geo coordinates not available for the requested propertyId.

500	
Internal Server Error

502	
Bad Gateway