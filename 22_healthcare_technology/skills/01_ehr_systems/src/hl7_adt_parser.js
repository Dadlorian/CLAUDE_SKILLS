/**
 * HL7 ADT Message Parser
 * Parses HL7 v2.x ADT messages and extracts patient demographic and visit information
 */

class HL7ADTParser {
  constructor(message) {
    this.message = message;
    this.segments = this.parseSegments(message);
  }

  /**
   * Parse HL7 message into segments
   */
  parseSegments(message) {
    const lines = message.split(/\r?\n/);
    const segments = {};

    lines.forEach(line => {
      if (line.trim()) {
        const fields = line.split('|');
        const segmentType = fields[0];

        if (!segments[segmentType]) {
          segments[segmentType] = [];
        }
        segments[segmentType].push(fields);
      }
    });

    return segments;
  }

  /**
   * Get field value with component/subcomponent support
   */
  getField(segment, fieldIndex, componentIndex = null, subcomponentIndex = null) {
    if (!this.segments[segment] || this.segments[segment].length === 0) {
      return null;
    }

    const segmentData = this.segments[segment][0];
    if (fieldIndex >= segmentData.length) {
      return null;
    }

    let value = segmentData[fieldIndex];

    // Handle components (separated by ^)
    if (componentIndex !== null && value) {
      const components = value.split('^');
      if (componentIndex < components.length) {
        value = components[componentIndex];
      } else {
        return null;
      }
    }

    // Handle subcomponents (separated by &)
    if (subcomponentIndex !== null && value) {
      const subcomponents = value.split('&');
      if (subcomponentIndex < subcomponents.length) {
        value = subcomponents[subcomponentIndex];
      } else {
        return null;
      }
    }

    return value || null;
  }

  /**
   * Parse message header (MSH segment)
   */
  parseMessageHeader() {
    return {
      sendingApplication: this.getField('MSH', 3),
      sendingFacility: this.getField('MSH', 4),
      receivingApplication: this.getField('MSH', 5),
      receivingFacility: this.getField('MSH', 6),
      messageDateTime: this.getField('MSH', 7),
      messageType: this.getField('MSH', 9, 0),
      triggerEvent: this.getField('MSH', 9, 1),
      messageControlId: this.getField('MSH', 10),
      processingId: this.getField('MSH', 11),
      versionId: this.getField('MSH', 12)
    };
  }

  /**
   * Parse event type (EVN segment)
   */
  parseEventType() {
    return {
      eventTypeCode: this.getField('EVN', 1),
      recordedDateTime: this.getField('EVN', 2),
      plannedEventDateTime: this.getField('EVN', 3),
      eventReasonCode: this.getField('EVN', 4),
      operatorId: this.getField('EVN', 5),
      eventOccurred: this.getField('EVN', 6)
    };
  }

  /**
   * Parse patient identification (PID segment)
   */
  parsePatientIdentification() {
    // Parse patient identifiers (can be multiple)
    const identifiers = [];
    const idField = this.getField('PID', 3);
    if (idField) {
      const idRepetitions = idField.split('~');
      idRepetitions.forEach(id => {
        const components = id.split('^');
        identifiers.push({
          id: components[0],
          checkDigit: components[1],
          checkDigitScheme: components[2],
          assigningAuthority: components[3],
          identifierType: components[4]
        });
      });
    }

    return {
      patientId: this.getField('PID', 2),
      patientIdentifierList: identifiers,
      mrn: identifiers.find(id => id.identifierType === 'MRN')?.id,
      ssn: identifiers.find(id => id.identifierType === 'SSN')?.id,
      patientName: {
        family: this.getField('PID', 5, 0),
        given: this.getField('PID', 5, 1),
        middle: this.getField('PID', 5, 2),
        suffix: this.getField('PID', 5, 3),
        prefix: this.getField('PID', 5, 4),
        full: `${this.getField('PID', 5, 1) || ''} ${this.getField('PID', 5, 0) || ''}`.trim()
      },
      mothersMaidenName: this.getField('PID', 6),
      dateOfBirth: this.getField('PID', 7),
      sex: this.getField('PID', 8),
      patientAlias: this.getField('PID', 9),
      race: this.getField('PID', 10),
      address: {
        street: this.getField('PID', 11, 0),
        otherDesignation: this.getField('PID', 11, 1),
        city: this.getField('PID', 11, 2),
        state: this.getField('PID', 11, 3),
        zip: this.getField('PID', 11, 4),
        country: this.getField('PID', 11, 5)
      },
      phoneHome: this.getField('PID', 13),
      phoneBusiness: this.getField('PID', 14),
      primaryLanguage: this.getField('PID', 15),
      maritalStatus: this.getField('PID', 16),
      religion: this.getField('PID', 17),
      accountNumber: this.getField('PID', 18),
      ssnNumber: this.getField('PID', 19)
    };
  }

  /**
   * Parse patient visit (PV1 segment)
   */
  parsePatientVisit() {
    return {
      patientClass: this.getField('PV1', 2),
      assignedPatientLocation: {
        pointOfCare: this.getField('PV1', 3, 0),
        room: this.getField('PV1', 3, 1),
        bed: this.getField('PV1', 3, 2),
        facility: this.getField('PV1', 3, 3)
      },
      admissionType: this.getField('PV1', 4),
      preadmitNumber: this.getField('PV1', 5),
      priorPatientLocation: this.getField('PV1', 6),
      attendingDoctor: {
        id: this.getField('PV1', 7, 0),
        familyName: this.getField('PV1', 7, 1),
        givenName: this.getField('PV1', 7, 2),
        degree: this.getField('PV1', 7, 6)
      },
      referringDoctor: {
        id: this.getField('PV1', 8, 0),
        familyName: this.getField('PV1', 8, 1),
        givenName: this.getField('PV1', 8, 2)
      },
      hospitalService: this.getField('PV1', 10),
      admitSource: this.getField('PV1', 14),
      visitNumber: this.getField('PV1', 19),
      dischargeDisposition: this.getField('PV1', 36),
      admitDateTime: this.getField('PV1', 44),
      dischargeDateTime: this.getField('PV1', 45)
    };
  }

  /**
   * Parse complete ADT message
   */
  parse() {
    return {
      messageHeader: this.parseMessageHeader(),
      eventType: this.parseEventType(),
      patient: this.parsePatientIdentification(),
      visit: this.parsePatientVisit()
    };
  }

  /**
   * Generate ACK (acknowledgment) message
   */
  generateACK(acknowledgmentCode = 'AA', textMessage = '') {
    const msh = this.parseMessageHeader();

    const ackSegments = [
      `MSH|^~\\&|${msh.receivingApplication}|${msh.receivingFacility}|${msh.sendingApplication}|${msh.sendingFacility}|${this.formatDateTime(new Date())}||ACK^${msh.triggerEvent}|${msh.messageControlId}_ACK|${msh.processingId}|${msh.versionId}`,
      `MSA|${acknowledgmentCode}|${msh.messageControlId}|${textMessage}`
    ];

    return ackSegments.join('\r');
  }

  formatDateTime(date) {
    return date.toISOString().replace(/[-:T.]/g, '').substring(0, 14);
  }
}

// Example usage
const sampleADT = `MSH|^~\\&|SENDING_APP|SENDING_FAC|RECEIVING_APP|RECEIVING_FAC|20231119120000||ADT^A01|MSG00001|P|2.5.1
EVN|A01|20231119120000|||REGCLERK
PID|1||MRN123456^^^FACILITY^MRN~SSN987654321^^^SSN||DOE^JOHN^ROBERT^JR^MR||19800115|M||W^White|123 MAIN ST^^ANYTOWN^CA^12345^USA|(555)555-1234|(555)555-5678||S|CHR|12345678|987-65-4321
PV1|1|I|3N^301^01^FACILITY|||123456^SMITH^JOHN^A^^DR^MD||||||MED||||123456^SMITH^JOHN^A^^DR^MD||V123456789|||||||||||||||||||||||20231119120000`;

const parser = new HL7ADTParser(sampleADT);
const parsedMessage = parser.parse();

console.log('Parsed ADT Message:');
console.log(JSON.stringify(parsedMessage, null, 2));

// Generate ACK
const ack = parser.generateACK('AA', 'Message accepted successfully');
console.log('\nGenerated ACK:');
console.log(ack);

module.exports = HL7ADTParser;
