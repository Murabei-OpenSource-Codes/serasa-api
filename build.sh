VERSION_FILE="version"
current_version=$(grep -E "^VERSION=" "$VERSION_FILE" | cut -d'=' -f2)
IFS='.' read -r major minor patch <<<"$current_version"
patch=$((patch + 1))
new_version="$major.$minor.$patch"
sed -i "s/^VERSION=.*/VERSION=$new_version/" "$VERSION_FILE"
echo "## Updated version to $new_version"

source $VERSION_FILE
sed -e 's#{VERSION}#'"${VERSION}"'#g' setup_template.py >setup.py

rm -R build/
python3 setup.py build sdist bdist_wheel

git add --all
git commit -m "Building a new version ${VERSION}"
git tag -a ${VERSION} -m "Building a new version ${VERSION}"
git push
git push origin ${VERSION}
