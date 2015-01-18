#!/usr/bin/env python

# CREDITS: This was copied from Sribharath Kainkaryam's https://github.com/srib/HobbyCode/blob/master/FetchBookFromDLI.py

import time
from argparse import ArgumentParser as ArgumentParser
from os import getcwd as GetCurrentWorkDir
from os.path import isdir as IsDirectory
from os import chdir as ChangeDirectory
from os import makedirs as MakeDirectory
from urllib import urlretrieve as FetchURL
from urlparse import urlparse as ParseURL
from urlparse import parse_qs as ParseQuery

def ParseCommandLineArgs():
    parser = ArgumentParser(description='Fetch TIFF files from DLI website and convert to PDF');
    parser.add_argument('DLIPath', metavar='Address of the webpage on DLI');
    parser.add_argument('-PDFPath', metavar='Location to save', default='CWD');
    parser.add_argument('-PDFName', metavar='Name of the PDF file',
	                            default='test.pdf');
    ParsedArguments = parser.parse_args()
    return ParsedArguments

def CheckSaveDir(ParsedArguments):

    if ParsedArguments.PDFPath == 'CWD':
	SaveDirectory = GetCurrentWorkDir();
	print 'PDF will be saved at ', SaveDirectory
    else:
	SaveDirectory = ParsedArguments.PDFPath;

	if not IsDirectory(SaveDirectory):
	    print SaveDirectory, 'is an invalid location'
	    SaveDirectory = GetCurrentWorkDir();
	    print 'PDF will be saved at ', SaveDirectory

    return SaveDirectory;

def MakeDir(SavePath):
    ChangeDirectory(SavePath);
    try:
	MakeDirectory('tmp')
    except OSError as exception:
	PathToTmp = SavePath+'/tmp';
	raise OSError('tmp exists. Delete the tmp folder first');

def GetDownloadPath(DLIPath):
    ParsedPath = ParseURL(DLIPath);
    ParsedQuery = ParseQuery(ParsedPath.query);
    DiskPath = " ";
    DiskPath = DiskPath.join(ParsedQuery['path1']);

    # Work around to avoid the space after join. Don't know why!
    d = ParsedPath.scheme+'://'+ParsedPath.netloc;
    d = d+DiskPath+'/PTIFF/';
    DownloadPath = d.replace(" ","");

    First = ParsedQuery['first'];
    Last = ParsedQuery['last'];

    StartPage = int(First[0])
    EndPage = int(Last[0])

    return StartPage, EndPage, DownloadPath


def FetchFiles(ParsedArguments):

    StartPage, EndPage, DownloadPath = GetDownloadPath(ParsedArguments.DLIPath);
    SavePath = CheckSaveDir(ParsedArguments);
    ChangeDirectory(SavePath);
    MakeDir(SavePath);
    ChangeDirectory('tmp');

    starttime = time.time()
    for PageNumber in range(StartPage, EndPage+1):
        print 'Fetching page number', PageNumber
        PageNum = str(format(PageNumber, '08'))
        FileName = PageNum+'.tif'
        FileURL = DownloadPath+FileName
        FetchURL(FileURL,FileName)

    endtime = time.time();
    print 'Time needed to fetch', endtime-starttime

def main():
    ParsedArguments = ParseCommandLineArgs();
    FetchFiles(ParsedArguments);

if __name__ == "__main__":
    main();
