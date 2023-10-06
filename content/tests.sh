title="This is a test 2388294"
description1="Description test"
description1="Description test2"
image_location="images/testimage.png"
# - Submit a new photo
echo '1 - Submit a new photo'
curl -s http://localhost:5001/create -F "title=${title}" -F "description=${description1}" -F "image=@${image_location}" -X POST -f >/dev/null ||  export fail=1
# Get the photo id of the one we just submitted
myphotoid=`curl http://localhost:5001/api/photos  -f 2>/dev/null |jq ".[] | select(.title==\"${title}\").id"`
# Check we can access the new photo
echo "2 - Check we can access the new photo"
curl -s http://localhost:5001/${myphotoid} -f  >/dev/null || export fail=1
# Edit the new photo
echo '3 - Edit the new photo'
curl -s http://localhost:5001/${myphotoid}/edit -F "title=${title}" -F "description=${description2}" -F "image=@${image_location}" -X POST -f >/dev/null  || export fail=1
# Delete the new photo
echo '4 - Delete the new photo'
curl -s http://localhost:5001/${myphotoid}/delete  -X POST -f >/dev/null || export fail=1

if [[ "$fail" == "1" ]]
then
   exit 1
else
   exit 0
fi
