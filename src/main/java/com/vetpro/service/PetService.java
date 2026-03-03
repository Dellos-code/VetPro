package com.vetpro.service;

import com.vetpro.model.Pet;
import com.vetpro.repository.PetRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class PetService {

    private final PetRepository petRepository;

    public PetService(PetRepository petRepository) {
        this.petRepository = petRepository;
    }

    public Pet createPet(Pet pet) {
        return petRepository.save(pet);
    }

    @Transactional(readOnly = true)
    public Optional<Pet> getPetById(Long id) {
        return petRepository.findById(id);
    }

    @Transactional(readOnly = true)
    public List<Pet> getPetsByOwner(Long ownerId) {
        return petRepository.findByOwnerId(ownerId);
    }

    @Transactional(readOnly = true)
    public Optional<Pet> getPetByMicrochip(String microchipNumber) {
        return petRepository.findByMicrochipNumber(microchipNumber);
    }

    public Pet updatePet(Long id, Pet updated) {
        Pet existing = petRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Pet not found"));
        existing.setName(updated.getName());
        existing.setSpecies(updated.getSpecies());
        existing.setBreed(updated.getBreed());
        existing.setDateOfBirth(updated.getDateOfBirth());
        existing.setGender(updated.getGender());
        existing.setMicrochipNumber(updated.getMicrochipNumber());
        existing.setOwner(updated.getOwner());
        return petRepository.save(existing);
    }

    public void deletePet(Long id) {
        petRepository.deleteById(id);
    }
}
