package com.vetpro.service;

import com.vetpro.model.Medication;
import com.vetpro.model.Prescription;
import com.vetpro.repository.MedicationRepository;
import com.vetpro.repository.PrescriptionRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class PrescriptionService {

    private final PrescriptionRepository prescriptionRepository;
    private final MedicationRepository medicationRepository;

    public PrescriptionService(PrescriptionRepository prescriptionRepository,
                               MedicationRepository medicationRepository) {
        this.prescriptionRepository = prescriptionRepository;
        this.medicationRepository = medicationRepository;
    }

    public Prescription createPrescription(Prescription prescription) {
        Prescription saved = prescriptionRepository.save(prescription);
        Medication medication = saved.getMedication();
        medication.setStockQuantity(Math.max(0, medication.getStockQuantity() - 1));
        medicationRepository.save(medication);
        return saved;
    }

    @Transactional(readOnly = true)
    public Optional<Prescription> getPrescriptionById(Long id) {
        return prescriptionRepository.findById(id);
    }

    @Transactional(readOnly = true)
    public List<Prescription> getPrescriptionsByRecord(Long recordId) {
        return prescriptionRepository.findByMedicalRecordId(recordId);
    }
}
