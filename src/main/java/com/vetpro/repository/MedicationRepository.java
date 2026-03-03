package com.vetpro.repository;

import com.vetpro.model.Medication;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface MedicationRepository extends JpaRepository<Medication, Long> {

    Optional<Medication> findByName(String name);

    List<Medication> findByStockQuantityLessThanEqual(Integer threshold);
}
