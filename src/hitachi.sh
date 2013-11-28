#! /bin/bash
###
# Set file names
###
SOURCE="RbwrTh.py" ;
PATCH="hitachi.patch" ;
DES3="${PATCH}.des3" ;
###
# Check for presence of files
###
[ ! -e "${SOURCE}" ] && echo "Error, ${SOURCE} must be present." && exit ;
[ ! -e "${DES3}" ] && echo "Error, ${DES3} must be present." && exit ;
###
# Decrypt patch file
###
[ -e "${PATCH}" ] && \rm -vf "${PATCH}" ;
openssl des3 -d < "${DES3}" > "${PATCH}" ;
###
# Patch RbwrTh.py, if decryption is successful
###
[ ! "${?}" -eq 0 ] && echo "Error, must provide correct decryption key." && exit ;
patch < "${PATCH}" ;
###
# Finish
###
[ "${?}" -eq 0 ] && echo "Patching of ${SOURCE} successfully completed!" ;
