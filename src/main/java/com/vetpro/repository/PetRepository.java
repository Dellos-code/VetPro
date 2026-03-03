package com.vetpro.repository;

import com.vetpro.model.Pet;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface PetRepository extends JpaRepository<Pet, Long> {

    List<Pet> findByOwnerId(Long ownerId);

    Optional<Pet> findByMicrochipNumber(String microchipNumber);
}
