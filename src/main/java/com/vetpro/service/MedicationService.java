package com.vetpro.service;

import com.vetpro.model.Medication;
import com.vetpro.repository.MedicationRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class MedicationService {

    private final MedicationRepository medicationRepository;

    public MedicationService(MedicationRepository medicationRepository) {
        this.medicationRepository = medicationRepository;
    }

    public Medication addMedication(Medication medication) {
        return medicationRepository.save(medication);
    }

    @Transactional(readOnly = true)
    public Optional<Medication> getMedicationById(Long id) {
        return medicationRepository.findById(id);
    }

    @Transactional(readOnly = true)
    public List<Medication> getAllMedications() {
        return medicationRepository.findAll();
    }

    public Medication updateStock(Long id, Integer quantity) {
        Medication medication = medicationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Medication not found"));
        medication.setStockQuantity(quantity);
        return medicationRepository.save(medication);
    }

    @Transactional(readOnly = true)
    public List<Medication> getLowStockMedications() {
        return medicationRepository.findAll().stream()
                .filter(m -> m.getStockQuantity() <= m.getReorderLevel())
                .toList();
    }

    public Medication updateMedication(Long id, Medication updated) {
        Medication existing = medicationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Medication not found"));
        existing.setName(updated.getName());
        existing.setDescription(updated.getDescription());
        existing.setStockQuantity(updated.getStockQuantity());
        existing.setUnitPrice(updated.getUnitPrice());
        existing.setReorderLevel(updated.getReorderLevel());
        return medicationRepository.save(existing);
    }
}
