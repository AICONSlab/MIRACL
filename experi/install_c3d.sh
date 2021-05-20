c3dpath=$( command -v c3d )
if [[ -z "${c3dpath}" ]]; then
	echo "Command c3d was not found. Downloading and installing software to ${SCRIPTPATH}/depends/c3d. Path will be added to PATH environment variable."
    mkdir -p "${SCRIPTPATH}/depends/c3d/"
    wget https://downloads.sourceforge.net/project/c3d/c3d/Nightly/c3d-nightly-Linux-x86_64.tar.gz && \
    tar -xzvf c3d-nightly-Linux-x86_64.tar.gz && mv c3d-1.1.0-Linux-x86_64/* "${SCRIPTPATH}/depends/c3d/" && \
    rm c3d-nightly-Linux-x86_64.tar.gz
    export PATH="${SCRIPTPATH}/depends/c3d/c3d-1.1.0-Linux-x86_64/bin/:$PATH"
fi
