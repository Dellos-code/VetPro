package com.vetpro.service;

import com.vetpro.model.MedicalRecord;
import com.vetpro.repository.MedicalRecordRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class MedicalRecordService {

    private final MedicalRecordRepository medicalRecordRepository;

    public MedicalRecordService(MedicalRecordRepository medicalRecordRepository) {
        this.medicalRecordRepository = medicalRecordRepository;
    }

    public MedicalRecord createRecord(MedicalRecord record) {
        return medicalRecordRepository.save(record);
    }

    @Transactional(readOnly = true)
    public Optional<MedicalRecord> getRecordById(Long id) {
        return medicalRecordRepository.findById(id);
    }

    @Transactional(readOnly = true)
    public List<MedicalRecord> getRecordsByPet(Long petId) {
        return medicalRecordRepository.findByPetId(petId);
    }

    @Transactional(readOnly = true)
    public List<MedicalRecord> getRecordsByVet(Long vetId) {
        return medicalRecordRepository.findByVeterinarianId(vetId);
    }
}
