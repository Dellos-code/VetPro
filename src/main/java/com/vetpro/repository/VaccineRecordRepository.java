package com.vetpro.repository;

import com.vetpro.model.VaccineRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface VaccineRecordRepository extends JpaRepository<VaccineRecord, Long> {

    List<VaccineRecord> findByPetId(Long petId);

    List<VaccineRecord> findByNextDueDateBefore(LocalDate date);
}
