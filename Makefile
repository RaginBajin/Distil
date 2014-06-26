
VERSION=0.1
NAME=openstack-distil
INSTALL_PATH=/opt/stack/distil
BINARY_PATH=/usr/local/bin

WORK_DIR=./work

CONF_DIR=${WORK_DIR}/${INSTALL_PATH}/etc/distil

clean:
	@rm -rf ./work
	@rm -f *.deb

init:
	@mkdir ./work/
	@mkdir -p ./work${INSTALL_PATH}
	@mkdir -p ./work${BINARY_PATH}

deb: clean init

	@cp -r ./distil \
		./scripts \
		./README.md \
		./INVOICES.md \
		requirements.txt \
		setup.py \
		${WORK_DIR}${INSTALL_PATH}
	@mkdir ${WORK_DIR}${INSTALL_PATH}/bin
	@cp     ./bin/web ./bin/web.py \
		${WORK_DIR}${INSTALL_PATH}/bin
	@chmod 0755 ${WORK_DIR}${INSTALL_PATH}/bin/web
	@mkdir -p ${CONF_DIR}
	@mkdir -p ${WORK_DIR}/etc/distil
	@cp ./examples/conf.yaml ${WORK_DIR}/etc/distil/conf.yaml
	@cp ./examples/real_rates.csv ${WORK_DIR}/etc/distil/real_rates.csv
	@fpm -s dir -t deb -n ${NAME} -v ${VERSION} \
	--depends 'libpq-dev' \
	--deb-pre-depends "libmysql++-dev" \
	--deb-pre-depends python2.7 \
	--deb-pre-depends python-pip \
	--deb-pre-depends python-dev \
	--deb-pre-depends python-virtualenv \
	--template-scripts  \
	--template-value install_path=${INSTALL_PATH} \
	-C ${WORK_DIR} \
	.
