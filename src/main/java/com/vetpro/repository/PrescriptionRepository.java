package com.vetpro.repository;

import com.vetpro.model.Prescription;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PrescriptionRepository extends JpaRepository<Prescription, Long> {

    List<Prescription> findByMedicalRecordId(Long recordId);

    List<Prescription> findByMedicationId(Long medicationId);
}
