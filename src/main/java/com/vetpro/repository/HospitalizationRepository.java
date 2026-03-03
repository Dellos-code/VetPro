package com.vetpro.repository;

import com.vetpro.model.Hospitalization;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface HospitalizationRepository extends JpaRepository<Hospitalization, Long> {

    List<Hospitalization> findByPetId(Long petId);

    List<Hospitalization> findByStatus(String status);

    List<Hospitalization> findByVeterinarianId(Long vetId);
}
