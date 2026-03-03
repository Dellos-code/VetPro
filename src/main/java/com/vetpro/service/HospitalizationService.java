package com.vetpro.service;

import com.vetpro.model.Hospitalization;
import com.vetpro.repository.HospitalizationRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class HospitalizationService {

    private final HospitalizationRepository hospitalizationRepository;

    public HospitalizationService(HospitalizationRepository hospitalizationRepository) {
        this.hospitalizationRepository = hospitalizationRepository;
    }

    public Hospitalization admitPet(Hospitalization hospitalization) {
        hospitalization.setStatus("ADMITTED");
        return hospitalizationRepository.save(hospitalization);
    }

    @Transactional(readOnly = true)
    public Optional<Hospitalization> getHospitalizationById(Long id) {
        return hospitalizationRepository.findById(id);
    }

    @Transactional(readOnly = true)
    public List<Hospitalization> getHospitalizationsByPet(Long petId) {
        return hospitalizationRepository.findByPetId(petId);
    }

    @Transactional(readOnly = true)
    public List<Hospitalization> getCurrentlyAdmitted() {
        return hospitalizationRepository.findByStatus("ADMITTED");
    }

    public Hospitalization dischargePet(Long id) {
        Hospitalization hospitalization = hospitalizationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Hospitalization not found"));
        hospitalization.setDischargeDate(LocalDateTime.now());
        hospitalization.setStatus("DISCHARGED");
        return hospitalizationRepository.save(hospitalization);
    }

    public Hospitalization updateDailyNotes(Long id, String notes) {
        Hospitalization hospitalization = hospitalizationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Hospitalization not found"));
        hospitalization.setDailyNotes(notes);
        return hospitalizationRepository.save(hospitalization);
    }
}
