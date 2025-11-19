/**
 * DICOM Parser using dicom-parser library
 * JavaScript/Node.js implementation for parsing DICOM files
 */

const dicomParser = require('dicom-parser');
const fs = require('fs');

class DICOMParser {
    constructor(filePath) {
        this.filePath = filePath;
        this.dataSet = null;
    }

    /**
     * Load and parse DICOM file
     */
    async parse() {
        const arrayBuffer = fs.readFileSync(this.filePath).buffer;
        const byteArray = new Uint8Array(arrayBuffer);
        
        try {
            this.dataSet = dicomParser.parseDicom(byteArray);
            return true;
        } catch (error) {
            console.error('Error parsing DICOM:', error);
            return false;
        }
    }

    /**
     * Get tag value safely
     */
    getTag(tag) {
        try {
            const element = this.dataSet.elements[tag];
            if (!element) return null;
            
            return this.dataSet.string(tag);
        } catch (error) {
            return null;
        }
    }

    /**
     * Extract patient demographics
     */
    getPatientInfo() {
        return {
            patientName: this.getTag('x00100010'),
            patientID: this.getTag('x00100020'),
            patientBirthDate: this.getTag('x00100030'),
            patientSex: this.getTag('x00100040')
        };
    }

    /**
     * Extract study information
     */
    getStudyInfo() {
        return {
            studyInstanceUID: this.getTag('x0020000d'),
            studyDate: this.getTag('x00080020'),
            studyTime: this.getTag('x00080030'),
            studyDescription: this.getTag('x00081030'),
            accessionNumber: this.getTag('x00080050')
        };
    }

    /**
     * Extract series information
     */
    getSeriesInfo() {
        return {
            seriesInstanceUID: this.getTag('x0020000e'),
            seriesNumber: this.getTag('x00200011'),
            modality: this.getTag('x00080060'),
            seriesDescription: this.getTag('x0008103e')
        };
    }

    /**
     * Extract pixel data information (not the actual pixels)
     */
    getImageInfo() {
        return {
            rows: this.dataSet.uint16('x00280010'),
            columns: this.dataSet.uint16('x00280011'),
            bitsAllocated: this.dataSet.uint16('x00280100'),
            bitsStored: this.dataSet.uint16('x00280101'),
            pixelRepresentation: this.dataSet.uint16('x00280103'),
            samplesPerPixel: this.dataSet.uint16('x00280002')
        };
    }

    /**
     * Get all metadata as JSON
     */
    getAllMetadata() {
        return {
            patient: this.getPatientInfo(),
            study: this.getStudyInfo(),
            series: this.getSeriesInfo(),
            image: this.getImageInfo()
        };
    }

    /**
     * Export metadata to JSON file
     */
    exportMetadata(outputPath) {
        const metadata = this.getAllMetadata();
        fs.writeFileSync(outputPath, JSON.stringify(metadata, null, 2));
        return metadata;
    }
}

// Example usage
async function main() {
    const parser = new DICOMParser('example.dcm');
    
    if (await parser.parse()) {
        console.log('Patient:', parser.getPatientInfo());
        console.log('Study:', parser.getStudyInfo());
        console.log('Series:', parser.getSeriesInfo());
        
        // Export to JSON
        parser.exportMetadata('metadata.json');
    }
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = DICOMParser;
