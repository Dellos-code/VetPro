package com.vetpro.service;

import com.vetpro.model.VaccineRecord;
import com.vetpro.repository.VaccineRecordRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;

@Service
@Transactional
public class VaccineRecordService {

    private final VaccineRecordRepository vaccineRecordRepository;

    public VaccineRecordService(VaccineRecordRepository vaccineRecordRepository) {
        this.vaccineRecordRepository = vaccineRecordRepository;
    }

    public VaccineRecord administerVaccine(VaccineRecord record) {
        return vaccineRecordRepository.save(record);
    }

    @Transactional(readOnly = true)
    public List<VaccineRecord> getRecordsByPet(Long petId) {
        return vaccineRecordRepository.findByPetId(petId);
    }

    @Transactional(readOnly = true)
    public List<VaccineRecord> getOverdueVaccinations(LocalDate asOfDate) {
        return vaccineRecordRepository.findByNextDueDateBefore(asOfDate);
    }
}
