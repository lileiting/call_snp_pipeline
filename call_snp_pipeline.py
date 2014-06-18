#!/usr/lib/python
#-*- coding:utf-8 -*-
import os
from subprocess import call

class FreebayesPipe:
    def __init__(self, dirname):
        self.dirname = dirname
        self.allnamelist = os.listdir(dirname)
        self.namelist = []
        self.arg1 = []
        self.arg2 = []
        self.arg3 = []
        self.arg4 = []

    def getgzfilelist(self):
        for fn in self.allnamelist:
            temp = os.path.join(self.dirname, fn)
            if (os.path.isfile(temp) and temp.split('.')[-1] == 'gz'):
                self.namelist.append(fn)
                self.namelist.sort()

    def rungzfile(self):
        f0 = open('run_gz.txt', 'w')
        for fn in self.namelist:
            f0.write('gzip -d ' + fn + '\n')
        f0.close()

    def getfqfilelist(self):
        for fn in self.allnamelist:
            temp = os.path.join(self.dirname, fn)
            if (os.path.isfile(temp)
                and temp.split('.')[-1] in ['fastq', 'fq']):
                self.namelist.append(fn)
                self.namelist.sort()

    def pre_bwa(self):
        refq_suffixes = ['fa', 'fasta']
        index_suffixes = ('amb', 'ann', 'bwt', 'pac', 'sa')
        all_suffixes = [i.split('.')[-1] for i in self.allnamelist]
        if set(refq_suffixes) & set(all_suffixes) :
            print 'Reference sequences file has found.'
            if set(index_suffixes).issubset(all_suffixes):
                print 'The index has been built.'
            else:
                print "The reference sequence don't build index yet. \
building..."
                for i in self.allnamelist:
                    if i.split('.')[-1] in refq_suffixes:
                        call(['bwa', 'index', i])
        else:
            print 'No reference sequences found in current directory, \
please check your files.'

    def runbwafile(self):
        L = range(0, len(self.namelist), 2)
        lib = 1
        for i in L:
            ID = 'flowcell1.lane' + \
self.namelist[i].split('00')[-1].split('_')[0]
            PL = 'illumina'
            LB = 'lib' + str(lib)
            lib += 1
            SM = self.namelist[i].split('-')[0][1:]
            R = r"'@RG\tID:%s\tSM:%s\tPL:%s\tLB:%s'"%(ID, SM, PL, LB)
            sam_prefix = '_'.join(self.namelist[i].split('_')[:-1])
            self.arg1.append(self.namelist[i])
            self.arg2.append(self.namelist[i+1])
            self.arg3.append(sam_prefix+'.sam')
            self.arg4.append(R)
        f0 = open('run_bwa.txt', 'w')
        for x, y, z, w in zip(self.arg1, self.arg2, self.arg3, self.arg4):
            f0.write('bwa mem -t 40 -R ' + w + ' Osativa_204.fa ' \
+ x + ' '+y + ' > ' + z + '\n')
        f0.close()

    def getsamfilelist(self):
        for fn in self.allnamelist:
            temp = os.path.join(self.dirname,fn)
            if (os.path.isfile(temp) and temp.split('.')[-1] == 'sam') :
                self.namelist.append(fn)
                self.namelist.sort()

    def runsam2bamfile(self):
        for i in self.namelist:
            self.arg1.append(i)
            self.arg2.append(i.split('.')[0] + '.bam')
        f0 = open('run_sam2bam.txt', 'w')
        for x, y in zip(self.arg1, self.arg2):
            f0.write('samtools view -bS ' + x + ' > ' + y + '\n')
        f0.close()

    def getbamfilelist(self):
        for fn in self.allnamelist:
            temp = os.path.join(self.dirname, fn)
            if (os.path.isfile(temp) and fn.split('.')[-1] == 'bam'
                and not set(['sorted', 'rmp', 'rg']) & set(fn.split('.')) ):
                self.namelist.append(fn)
                self.namelist.sort()

    def runsortfile(self):
        for i in self.namelist:
            self.arg1.append(i)
            self.arg2.append(i.split('.')[0] + '.sorted')
        f0 = open('run_sort.txt', 'w')
        for x, y in zip(self.arg1, self.arg2):
            f0.write('samtools sort ' + x + ' ' + y + '\n')
        f0.close()

    def getsortfilelist(self):
        for fn in self.allnamelist:
            temp = os.path.join(self.dirname, fn)
            if (os.path.isfile(temp)
                and fn.split('.')[-2:] == ['sorted', 'bam']
                and not set(['rmp', 'rg']) & set(fn.split('.')) ):
                self.namelist.append(fn)
                self.namelist.sort()

    def runrmdupfile(self):
        for i in self.namelist:
            self.arg1.append(i)
            self.arg2.append(i.split('.')[0] + '.sorted.rmp.bam')
        f0 = open('run_rmp.txt', 'w')
        for x, y in zip(self.arg1, self.arg2):
            f0.write('samtools rmdup ' + x + ' ' + y + '\n')
        f0.close()

    def getrmpfilelist(self):
        for fn in self.allnamelist:
            temp = os.path.join(self.dirname, fn)
            if (os.path.isfile(temp)
                and fn.split('.')[-3:] == ['sorted', 'rmp', 'bam']
                and 'rg' not in fn.split('.')):
                self.namelist.append(fn)
                self.namelist.sort()

    def runaddrgfile(self):
        for i in self.namelist:
            self.arg1.append(i)
            rg_name = i.split('-')[0][1:]
            self.arg3.append(i.split('.')[0] + '.sorted.rmp.rg.bam')
        f0 = open('run_addrg.txt', 'w')
        for x, y in zip(self.arg1, self.arg3):
            f0.write('bamaddrg -b ' + x + ' -s ' + rg_name + ' > ' + y + '\n')
        f0.close()

    def getrgfilelist(self):
        for fn in self.allnamelist:
            seg = fn.split('.')
            temp = os.path.join(self.dirname, fn)
            if (os.path.isfile(temp)
                and seg[-4:] == ['sorted', 'rmp', 'rg', 'bam']):
                self.namelist.append(fn)
                self.namelist.sort()

    def getrecalfilelist(self):
        for fn in self.allnamelist:
            seg = fn.split('.')
            temp = os.path.join(self.dirname, fn)
            if (os.path.isfile(temp)
                and seg[1:] == ['sorted','rmp','rg','recal', 'bam']):
                self.namelist.append(fn)
                self.namelist.sort()

    def runbaifile(self):
        for i in self.namelist:
            self.arg1.append(i)
        f0 = open('run_bai.txt', 'w')
        for x in self.arg1:
            f0.write('samtools index ' + x + '\n')
        f0.close()

    def pre_ref(self):
        refq_suffixes = ['fa', 'fasta']
        all_suffixes = [i.split('.')[-1] for i in self.allnamelist]
        if set(refq_suffixes) & set(all_suffixes) :
            print 'Reference sequences file has found.'
            for i in self.allnamelist:
                if i.split('.')[-1] in refq_suffixes:
                    ref = i
            if 'fai' not in all_suffixes:
                call(['samtools', 'faidx', ref])
                print 'faidx already'
            elif 'dict' not in all_suffixes:
                call(['java', '-jar', '/share/Public/cmiao/picard-tools-1.112\
/CreateSequenceDictionary.jar', 'R=' + ref, 'O=' + ref.split('.')[0] + \
'.dict'])
                print 'dict already'
            else:
                print 'All the dependencies have prepared.'
        else:
            print 'Reference sequence file is not exist.'

#if __name__ == '__main__':
#    step1 = FreebayesPipe('.')
#    step1.getgzfilelist()
#    if step1.namelist:
#        print step1.namelist
#        step1.rungzfile()
#        call('parallel < run_gz.txt', shell = True)

#    step2 = FreebayesPipe('.')
#    step2.getfqfilelist()
#    print step2.namelist
#    step2.pre_bwa()
#    step2.runbwafile()
#    call('parallel < run_bwa.txt', shell = True)

#    step3 = FreebayesPipe('.')
#    step3.getsamfilelist()
#    print step3.namelist
#    step3.runsam2bamfile()
#    call('parallel < run_sam2bam.txt', shell = True)

#    step4 = FreebayesPipe('.')
#    step4.getbamfilelist()
#    print step4.namelist
#    step4.runsortfile()
#    call('parallel < run_sort.txt', shell = True)

#    step5 = FreebayesPipe('.')
#    step5.getsortfilelist()
#    print step5.namelist
#    step5.runrmdupfile()
#    call('parallel < run_rmp.txt', shell = True)

#    step6 = FreebayesPipe('.')
#    step6.getrmpfilelist()
#    print step6.namelist
#    step6.runaddrgfile()
#    call('parallel < run_addrg.txt', shell = True)

#    step7 = FreebayesPipe('.')
#    step7.getrmpfilelist()
#    print step7.namelist
#    step7.runbaifile()
#    call('parallel < run_bai.txt', shell = True)