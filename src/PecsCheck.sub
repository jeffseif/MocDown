#! /bin/bash
#SBATCH --cpu_bind=verbose,rank_ldom
#SBATCH --cpus-per-task=6
#SBATCH --error=PecsCheck.e%j
#SBATCH --mem_bind=verbose,local
#SBATCH --job-name=PecsCheck
#SBATCH --ntasks=8
#SBATCH --output=PecsCheck.o%j
#SBATCH --partition=x
#SBATCH --time=10-0

# Verify module loading of icc-x86_64/intel-amd64, mvapich2-1.8.1, mcnp6b2, mcnpbindata-6b2
. /etc/bashrc ;
which mcnp6.mpi &> /dev/null || module load icc-x86_64/intel-amd64 mvapich2-1.8.1 mcnp6b2 mcnpbindata-6b2 ;

# PecsCheck run command
[ -e PecsCheck.log ] && rm -vf PecsCheck.log ;
./PecsCheck.py inp1 > PecsCheck.log ;
